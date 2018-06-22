//
// This code is not in an action because then our target does not support ``if''
//

bit<32> frequency;
bit<32> cnt;
bit<32> next;

secpar.read(frequency, 0);
pktcnt.read(cnt, 0);
nextcopy.read(next, 0);

if (frequency > 0 && next <= cnt) {
  do_copy();

  // ensure that next is not lagging, e.g., because secpar=0 at some point
  next = cnt;

  // deal with counter overflow 
  if (next+frequency < next) {
    next = 0;
    cnt = 0;
  }

  // schedule next packet to be copied
  nextcopy.write(0, next+frequency);
}
pktcnt.write(0, cnt+1);
