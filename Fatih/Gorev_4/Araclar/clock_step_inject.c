/*
 * Synthetic, process-local backward CLOCK_REALTIME step for an isolated gNB
 * regression test. No operating-system clock-setting API is used.
 *
 * Build (Linux):
 *   cc -std=c11 -O2 -Wall -Wextra -fPIC -shared \
 *      -o clock_step_inject.so clock_step_inject.c -ldl
 *
 * Apply LD_PRELOAD to the gNB command itself, never export it globally:
 *   env LD_PRELOAD=/absolute/path/clock_step_inject.so \
 *       /absolute/path/gnb_compat -c /absolute/path/test.yml
 *
 * This intercepts clock_gettime(), including the usual libstdc++
 * system_clock::now() path. It does not intercept gettimeofday(), direct
 * syscalls, or direct vDSO calls. The activation marker in stderr proves the
 * clock_gettime() hook has actually applied its first offset.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <limits.h>
#include <stdatomic.h>
#include <stddef.h>
#include <string.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

typedef int (*clock_gettime_function)(clockid_t, struct timespec *);

static clock_gettime_function real_clock_gettime;
static struct timespec start_monotonic;
static int enabled;
static atomic_int stepped = ATOMIC_VAR_INIT(0);

/* During loader initialization dlsym may not be ready yet. The fallback reads
 * a clock using a syscall; it never sets or adjusts any clock. */
static int read_original_clock(clockid_t clock_id, struct timespec *result)
{
    if (real_clock_gettime != NULL) {
        return real_clock_gettime(clock_id, result);
    }
    return (int)syscall(SYS_clock_gettime, clock_id, result);
}

__attribute__((constructor))
static void initialize_clock_step(void)
{
    char executable[PATH_MAX];
    const char *basename;
    ssize_t length;
    const int saved_errno = errno;

    real_clock_gettime =
        (clock_gettime_function)dlsym(RTLD_NEXT, "clock_gettime");

    length = readlink("/proc/self/exe", executable, sizeof(executable) - 1);
    if (length <= 0 || (size_t)length >= sizeof(executable) - 1) {
        errno = saved_errno;
        return;
    }
    executable[length] = '\0';
    basename = strrchr(executable, '/');
    basename = basename != NULL ? basename + 1 : executable;

    /* The executable itself must be named gnb, gnb_compat, gnb_clockguard,
     * etc. Merely renaming argv[0] or invoking a shell does not enable it. */
    if (strncmp(basename, "gnb", 3) == 0 &&
        read_original_clock(CLOCK_MONOTONIC, &start_monotonic) == 0) {
        enabled = 1;
    }
    errno = saved_errno;
}

int clock_gettime(clockid_t clock_id, struct timespec *result)
{
    struct timespec monotonic_now;
    int result_code;
    int saved_errno;

    /* Keep the original failure behavior and leave every other clock alone. */
    result_code = read_original_clock(clock_id, result);
    if (result_code != 0 || !enabled || clock_id != CLOCK_REALTIME) {
        return result_code;
    }
    saved_errno = errno;

    if (!atomic_load_explicit(&stepped, memory_order_acquire) &&
        read_original_clock(CLOCK_MONOTONIC, &monotonic_now) == 0) {
        const time_t elapsed_seconds =
            monotonic_now.tv_sec - start_monotonic.tv_sec;
        const int five_seconds_elapsed =
            elapsed_seconds > 5 ||
            (elapsed_seconds == 5 &&
             monotonic_now.tv_nsec >= start_monotonic.tv_nsec);

        if (five_seconds_elapsed &&
            atomic_exchange_explicit(&stepped, 1, memory_order_acq_rel) == 0) {
            static const char marker[] =
                "[clock-step-inject] Applied synthetic process-local "
                "CLOCK_REALTIME offset -2s after >=5s of CLOCK_MONOTONIC; "
                "offset persists; OS clocks are unchanged.\n";
            /* A failed marker write must not change the clock API result. */
            (void)write(STDERR_FILENO, marker, sizeof(marker) - 1);
        }
    }

    if (atomic_load_explicit(&stepped, memory_order_acquire)) {
        /* Subtracting whole seconds preserves a valid tv_nsec. No later
         * compensating forward jump is introduced in this process. */
        result->tv_sec -= 2;
    }
    errno = saved_errno;
    return result_code;
}
