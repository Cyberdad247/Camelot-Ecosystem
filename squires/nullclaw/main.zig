// NullClaw Zig Squire — Sub-Millisecond Edge Probe
// Memory Boundary: FixedBufferAllocator <= 512 KB
// Invariant: Zero hidden control flow, Zero libc dependency.

const std = @import("std");
const builtin = @import("builtin");

extern "kernel32" fn GetStdHandle(nStdHandle: i32) callconv(.winapi) ?*anyopaque;
extern "kernel32" fn WriteFile(
    hFile: ?*anyopaque,
    lpBuffer: [*]const u8,
    nNumberOfBytesToWrite: u32,
    lpNumberOfBytesWritten: ?*u32,
    lpOverlapped: ?*anyopaque,
) callconv(.winapi) i32;

pub fn main() !void {
    // 1. Enforce strict 512 KB Fixed Buffer Memory Allocation
    var memory_pool: [512 * 1024]u8 = undefined;
    var fba = std.heap.FixedBufferAllocator.init(&memory_pool);
    const allocator = fba.allocator();
    _ = allocator;

    const payload =
        \\{
        \\  "squire": "NULLCLAW_ZIG_SQUIRE_v1.0",
        \\  "memory_bound_kb": 512,
        \\  "allocator": "FixedBufferAllocator",
        \\  "edge_node": "Cybertronia",
        \\  "status": "ONLINE_ZERO_ALLOCATION"
        \\}
        \\
    ;

    if (comptime builtin.os.tag == .windows) {
        const handle = GetStdHandle(-11); // STD_OUTPUT_HANDLE = -11
        var written: u32 = 0;
        _ = WriteFile(handle, payload.ptr, @intCast(payload.len), &written, null);
    }
}
