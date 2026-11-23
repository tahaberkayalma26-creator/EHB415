#define _GNU_SOURCE
#include <time.h>
#include <stdio.h>
#include <stdint.h>
#include <sched.h>

static int64_t ns(clockid_t c) {
  struct timespec t; clock_gettime(c,&t);
  return (int64_t)t.tv_sec*1000000000LL+t.tv_nsec;
}
int main(void) {
  int64_t start=ns(CLOCK_MONOTONIC),last=ns(CLOCK_REALTIME),n=0,back=0,slot_back=0;
  while(ns(CLOCK_MONOTONIC)-start<8000000000LL) {
    int64_t now=ns(CLOCK_REALTIME);
    if(now<last) {
      back++;
      if(now/500000LL<last/500000LL)slot_back++;
      if(back<=20)printf("BACKWARD_NS=%lld CURRENT_NS=%lld CPU=%d\n",(long long)(now-last),(long long)now,sched_getcpu());
    }
    last=now;n++;
    if((n&1023)==0) { struct timespec pause={0,1000};nanosleep(&pause,0); }
  }
  printf("SAMPLES=%lld BACKWARD=%lld BACKWARD_500US_SLOT=%lld\n",(long long)n,(long long)back,(long long)slot_back);
  return 0;
}
