#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct data_t {
    u32 pid;        // Process ID
    int libcallno;  // Library call number (from syscall argument)
};

BPF_PERF_OUTPUT(events);

int syscall__dummy(struct pt_regs *ctx, int libcallno) {
    struct data_t data = {};
    
    // Capture the PID
    data.pid = bpf_get_current_pid_tgid() >> 32;

    data.libcallno = libcallno;

    // Send data to user-space
    events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
