#include <cstdint>
#include <cstddef>
#include <iostream>

#if defined(_MSC_VER)
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT __attribute__((visibility("default")))
#endif

extern "C" {

struct MerlinCConfig {
    const char* stun_server_url;
    const char* shm_name;
    size_t shm_capacity_bytes;
};

typedef void* MerlinWebRTCHandle;

EXPORT MerlinWebRTCHandle merlin_webrtc_create(const struct MerlinCConfig* config) {
    std::cout << "[NativeWebRTC] Created WebRTC Engine Context (Stub)" << std::endl;
    // Return a dummy pointer
    return (void*)0xDEADBEEF;
}

EXPORT int merlin_webrtc_initialize(MerlinWebRTCHandle handle) {
    std::cout << "[NativeWebRTC] Initialized WebRTC Engine (Stub)" << std::endl;
    return 1; // Success
}

EXPORT const char* merlin_webrtc_create_offer(MerlinWebRTCHandle handle) {
    return "{\"type\": \"offer\", \"sdp\": \"v=0\\n...\"}";
}

EXPORT int merlin_webrtc_process_answer(MerlinWebRTCHandle handle, const char* sdp_answer_json) {
    return 1;
}

EXPORT int merlin_webrtc_get_shm_fd(MerlinWebRTCHandle handle) {
    return 999; // Mock FD
}

EXPORT void merlin_webrtc_destroy(MerlinWebRTCHandle handle) {
    std::cout << "[NativeWebRTC] Destroyed WebRTC Engine Context (Stub)" << std::endl;
}

}
