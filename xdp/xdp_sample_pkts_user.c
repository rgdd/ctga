/* This program is free software; you can redistribute it and/or
 * modify it under the terms of version 2 of the GNU General Public
 * License as published by the Free Software Foundation.
 */
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <fcntl.h>
#include <poll.h>
#include <linux/perf_event.h>
#include <linux/bpf.h>
#include <net/if.h>
#include <errno.h>
#include <assert.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <time.h>
#include <signal.h>
#include <libbpf.h>
#include "bpf_load.h"
#include "bpf_util.h"
#include <bpf/bpf.h>

#include "perf-sys.h"
#include "trace_helpers.h"

#define SAMPLE_SIZE 420

static int pmu_fd, if_idx = 0;
static char *if_name;
static unsigned long long pktcounter;

static int do_attach(int idx, int fd, const char *name)
{
  int err;

  err = bpf_set_link_xdp_fd(idx, fd, 0);
  if (err < 0) {
    printf("ERROR: failed to attach program to %s\n", name);
  }

  return err;
}

static int do_detach(int idx, const char *name)
{
  int err;
  printf("Total Received Packets: %llu\n", pktcounter);

  err = bpf_set_link_xdp_fd(idx, -1, 0);
  if (err < 0) {
    printf("ERROR: failed to detach program from %s\n", name);
  }

  return err;
}

//
// From here aggregated traffic could be sent to a challenging component. See
// examples on how to inspect the sampled packets below.
//
static int print_bpf_output(void *data, int size)
{
  int i;
  struct {
    __u16 pkt_len;
    __u8  pkt_data[SAMPLE_SIZE];
  } __attribute__((packed)) *e = data;

  for (i = 0; i < e->pkt_len; i++) {
    printf("%02x ", e->pkt_data[i]);
  }
  printf("\n\n");

  return LIBBPF_PERF_EVENT_CONT;
}

static void test_bpf_perf_event(void)
{
  struct perf_event_attr attr = {
    .sample_type = PERF_SAMPLE_RAW,
    .type = PERF_TYPE_SOFTWARE,
    .config = PERF_COUNT_SW_BPF_OUTPUT,
  };
  int key = 0;

  pmu_fd = sys_perf_event_open(&attr, -1/*pid*/, 0/*cpu*/, -1/*group_fd*/, 0);

  assert(pmu_fd >= 0);
  assert(bpf_map_update_elem(map_fd[0], &key, &pmu_fd, BPF_ANY) == 0);
  ioctl(pmu_fd, PERF_EVENT_IOC_ENABLE, 0);
}

static void sig_handler(int signo)
{
  do_detach(if_idx, if_name);
  exit(0);
}

int main(int argc, char **argv)
{
  char filename[256];
  int ret, err;

  if (argc < 2) {
    printf("Usage: %s <ifname>\n", argv[0]);
    return 1;
  }

  snprintf(filename, sizeof(filename), "%s_kern.o", argv[0]);

  if (load_bpf_file(filename)) {
    printf("%s", bpf_log_buf);
    return 1;
  }

  if_idx = if_nametoindex(argv[1]);
  if (!if_idx) {
    if_idx = strtoul(argv[1], NULL, 0);
  }

  if (!if_idx) {
    fprintf(stderr, "Invalid ifname\n");
    return 1;
  }
  if_name = argv[1];
  err = do_attach(if_idx, prog_fd[0], argv[1]);
  if (err) {
    return err;
  }

  if (signal(SIGINT, sig_handler) ||
      signal(SIGHUP, sig_handler) ||
      signal(SIGTERM, sig_handler)) {
    perror("signal");
    return 1;
  }

  test_bpf_perf_event();

  if (perf_event_mmap(pmu_fd) < 0) {
    return 1;
  }

  ret = perf_event_poller(pmu_fd, print_bpf_output);
  kill(0, SIGINT);
  return ret;
}
