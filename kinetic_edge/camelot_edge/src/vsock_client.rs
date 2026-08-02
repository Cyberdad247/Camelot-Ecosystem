// Injected AF_VSOCK client connector to establish point-to-point connection
// from the guest Firecracker VM to the host Go vsock_multiplexer server.

pub struct VsockClient {
    cid: u32,
    port: u32,
}

impl VsockClient {
    pub fn new(cid: u32, port: u32) -> Self {
        Self { cid, port }
    }

    /// Establish a connection using raw AF_VSOCK sockets.
    pub fn connect(&self) -> Result<std::fs::File, Box<dyn std::error::Error>> {
        #[cfg(target_os = "linux")]
        {
            use libc::{socket, connect, sockaddr_vm, AF_VSOCK, SOCK_STREAM};
            use std::os::unix::io::FromRawFd;

            unsafe {
                // 1. Create raw AF_VSOCK socket
                let fd = socket(AF_VSOCK, SOCK_STREAM, 0);
                if fd < 0 {
                    return Err(std::io::Error::last_os_error().into());
                }

                // 2. Initialize sockaddr_vm structure
                let mut addr: sockaddr_vm = std::mem::zeroed();
                addr.svm_family = AF_VSOCK as u16;
                addr.svm_cid = self.cid;
                addr.svm_port = self.port;

                // 3. Connect to multiplexer
                let addr_ptr = &addr as *const sockaddr_vm as *const libc::sockaddr;
                let addr_len = std::mem::size_of::<sockaddr_vm>() as libc::socklen_t;
                
                if connect(fd, addr_ptr, addr_len) < 0 {
                    libc::close(fd);
                    return Err(std::io::Error::last_os_error().into());
                }

                Ok(std::fs::File::from_raw_fd(fd))
            }
        }
        #[cfg(not(target_os = "linux"))]
        {
            // Fallback for non-Linux / WASM host development (returns a dummy file)
            let temp_path = std::env::temp_dir().join(format!("vsock_mock_{}.tmp", self.port));
            let file = std::fs::OpenOptions::new()
                .read(true)
                .write(true)
                .create(true)
                .truncate(true)
                .open(temp_path)?;
            Ok(file)
        }
    }
}
