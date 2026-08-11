import os
import logging
from cffi import FFI

logger = logging.getLogger("MerlinNativeWebRTC")
ffi = FFI()

ffi.cdef("""
    typedef void* MerlinWebRTCHandle;

    struct MerlinCConfig {
        const char* stun_server_url;
        const char* shm_name;
        size_t shm_capacity_bytes;
    };

    MerlinWebRTCHandle merlin_webrtc_create(const struct MerlinCConfig* config);
    int merlin_webrtc_initialize(MerlinWebRTCHandle handle);
    const char* merlin_webrtc_create_offer(MerlinWebRTCHandle handle);
    int merlin_webrtc_process_answer(MerlinWebRTCHandle handle, const char* sdp_answer_json);
    int merlin_webrtc_get_shm_fd(MerlinWebRTCHandle handle);
    void merlin_webrtc_destroy(MerlinWebRTCHandle handle);
""")

SEARCH_PATHS = [
    "/usr/local/lib/libmerlin_webrtc_native.so",
    os.path.join(os.getcwd(), "build/native/libmerlin_webrtc_native.so"),
    "libmerlin_webrtc_native.so"
]

_c_lib = None
for path in SEARCH_PATHS:
    try:
        _c_lib = ffi.dlopen(path)
        logger.info(f"Loaded native WebRTC library from: {path}")
        break
    except OSError:
        continue

if _c_lib is None:
    logger.warning("libmerlin_webrtc_native.so not found. C++ acceleration disabled.")


class NativeWebRTCEngine:
    def __init__(
        self, 
        stun_url: str = "stun:stun.l.google.com:19302", 
        shm_name: str = "merlin_native_webrtc_pcm", 
        shm_capacity: int = 1048576
    ):
        if _c_lib is None:
            raise RuntimeError("C++ shared library libmerlin_webrtc_native.so is not loaded.")

        self._stun_url_bytes = stun_url.encode("utf-8")
        self._shm_name_bytes = shm_name.encode("utf-8")

        self.config = ffi.new("struct MerlinCConfig*", {
            "stun_server_url": ffi.new("char[]", self._stun_url_bytes),
            "shm_name": ffi.new("char[]", self._shm_name_bytes),
            "shm_capacity_bytes": shm_capacity
        })

        self.handle = _c_lib.merlin_webrtc_create(self.config)
        if self.handle == ffi.NULL:
            raise RuntimeError("Failed to allocate NativeWebRTC handle.")

        self.is_initialized = False

    def initialize(self) -> bool:
        status = _c_lib.merlin_webrtc_initialize(self.handle)
        self.is_initialized = (status == 1)
        return self.is_initialized

    def get_shm_fd(self) -> int:
        if not self.handle or self.handle == ffi.NULL:
            return -1
        return _c_lib.merlin_webrtc_get_shm_fd(self.handle)

    def close(self):
        if hasattr(self, "handle") and self.handle != ffi.NULL:
            _c_lib.merlin_webrtc_destroy(self.handle)
            self.handle = ffi.NULL

    def __del__(self):
        self.close()
