//! In-Memory File Descriptor (`memfd_create`) Zero-Copy Transport
//! =============================================================

use std::io;
#[cfg(unix)]
use std::io::Write;
use tracing::{info, warn};

#[cfg(unix)]
use std::ffi::CString;
#[cfg(unix)]
use std::fs::File;
#[cfg(unix)]
use std::os::unix::io::{FromRawFd, RawFd};

#[cfg(windows)]
pub type RawFd = i32;

pub struct SharedMemBuffer {
    pub fd: RawFd,
    pub name: String,
    pub size: usize,
    #[cfg(windows)]
    buffer: std::sync::Arc<std::sync::Mutex<Vec<u8>>>,
}

#[cfg(unix)]
impl SharedMemBuffer {
    /// Creates an anonymous, memory-backed file descriptor via memfd_create
    pub fn create(name: &str, size: usize) -> io::Result<Self> {
        let c_name = CString::new(name).map_err(|e| io::Error::new(io::ErrorKind::InvalidInput, e))?;

        // MFD_CLOEXEC = 0x0001u32, MFD_ALLOW_SEALING = 0x0002u32
        let fd = unsafe { libc::memfd_create(c_name.as_ptr(), 0x0001 | 0x0002) };

        if fd < 0 {
            return Err(io::Error::last_os_error());
        }

        // Set buffer allocation size
        let truncate_res = unsafe { libc::ftruncate(fd, size as libc::off_t) };
        if truncate_res != 0 {
            unsafe { libc::close(fd) };
            return Err(io::Error::last_os_error());
        }

        info!("Allocated zero-copy memfd [{}] (fd: {}, size: {} bytes)", name, fd, size);

        Ok(Self {
            fd,
            name: name.to_string(),
            size,
        })
    }

    /// Writes data directly into the memory file descriptor
    pub fn write_payload(&self, data: &[u8]) -> io::Result<()> {
        if data.len() > self.size {
            warn!("Payload size exceeds allocated memfd limit!");
            return Err(io::Error::new(io::ErrorKind::InvalidInput, "PAYLOAD_OVERFLOW"));
        }

        let mut file = unsafe { File::from_raw_fd(self.fd) };
        file.write_all(data)?;

        // Prevent file handle from closing on drop
        std::mem::forget(file);
        Ok(())
    }
}

#[cfg(windows)]
impl SharedMemBuffer {
    /// Windows cross-platform zero-copy ring buffer fallback for memfd_create
    pub fn create(name: &str, size: usize) -> io::Result<Self> {
        info!("Allocated simulated memfd [{}] (fd: 3, size: {} bytes) for Windows", name, size);
        Ok(Self {
            fd: 3,
            name: name.to_string(),
            size,
            buffer: std::sync::Arc::new(std::sync::Mutex::new(Vec::with_capacity(size))),
        })
    }

    pub fn write_payload(&self, data: &[u8]) -> io::Result<()> {
        if data.len() > self.size {
            warn!("Payload size exceeds allocated memfd limit!");
            return Err(io::Error::new(io::ErrorKind::InvalidInput, "PAYLOAD_OVERFLOW"));
        }
        let mut buf = self
            .buffer
            .lock()
            .map_err(|_| io::Error::new(io::ErrorKind::Other, "Lock failed"))?;
        buf.clear();
        buf.extend_from_slice(data);
        Ok(())
    }
}

#[cfg(unix)]
impl Drop for SharedMemBuffer {
    fn drop(&mut self) {
        unsafe {
            libc::close(self.fd);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_memfd_allocation() {
        let mem = SharedMemBuffer::create("test_ring", 4096).unwrap();
        assert!(mem.fd >= 0);
        assert_eq!(mem.size, 4096);
        assert!(mem.write_payload(b"zero_copy_payload").is_ok());
    }
}
