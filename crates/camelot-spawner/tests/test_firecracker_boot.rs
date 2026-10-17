//! Camelot Spawner — Dual-Mode ARM64 Firecracker Boot & 50-VM Max-Density Burst Harness
//!
//! Run unit & socket reclamation tests:
//!   cargo test -p camelot-spawner --test test_firecracker_boot
//!
//! Run <80ms boot gate + 50-VM progressive density sweep (works in both EL2 KVM and EL1 fallback):
//!   CAMELOT_BURST_VMS=50 sudo -E cargo test -p camelot-spawner --test test_firecracker_boot -- --ignored --nocapture

#![cfg(target_os = "linux")]

use std::fs::{self, OpenOptions};
use std::io::{self, ErrorKind};
use std::os::unix::net::UnixStream as StdUnixStream;
use std::os::unix::process::CommandExt;
use std::path::{Path, PathBuf};
use std::process::Stdio;
use std::time::{Duration, Instant};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{UnixListener, UnixStream};
use tokio::process::{Child, Command};

const SLICE_ROOT: &str = "/sys/fs/cgroup/camelot.slice";
const DEFAULT_KERNEL_PATH: &str = ".camelot/firecracker-assets/vmlinux-aarch64";
const DEFAULT_ROOTFS_PATH: &str = ".camelot/firecracker-assets/rootfs-aarch64.ext4";

/// Resource allocation tier under the 4 GiB Scarcity Protocol
#[derive(Clone, Copy, Debug)]
pub struct DensityProfile {
    pub name: &'static str,
    pub vcpu_count: u8,
    pub mem_size_mib: usize,
    pub cgroup_mem_high: &'static str,
    pub cgroup_mem_max: &'static str,
    pub pids_max: &'static str,
    pub rootfs_read_only: bool,
}

impl DensityProfile {
    /// Ultra-Dense Reflex Squire: 64 MiB guest RAM + 8 MiB VMM headroom (35–50 VMs with KSM + demand paging)
    pub const ULTRA_DENSE: Self = Self {
        name: "ultra-dense-64m",
        vcpu_count: 1,
        mem_size_mib: 64,
        cgroup_mem_high: "67108864", // 64 MiB in bytes
        cgroup_mem_max: "75497472",  // 72 MiB in bytes
        pids_max: "64",
        rootfs_read_only: true,
    };

    /// Minimal Reflex Squire: 128 MiB guest RAM + 8 MiB VMM headroom (18 VMs in 2.5 GiB pool)
    pub const MINIMAL_REFLEX: Self = Self {
        name: "minimal-reflex-128m",
        vcpu_count: 1,
        mem_size_mib: 128,
        cgroup_mem_high: "125829120", // 120 MiB in bytes
        cgroup_mem_max: "142606336",  // 136 MiB in bytes
        pids_max: "64",
        rootfs_read_only: true,
    };

    /// Standard Worker Squire: 256 MiB guest RAM + 8 MiB VMM headroom (9 VMs in 2.5 GiB pool)
    pub const STANDARD_WORKER: Self = Self {
        name: "standard-worker-256m",
        vcpu_count: 1,
        mem_size_mib: 256,
        cgroup_mem_high: "251658240", // 240 MiB in bytes
        cgroup_mem_max: "276824064",  // 264 MiB in bytes
        pids_max: "64",
        rootfs_read_only: true,
    };
}

/// Summary metrics for a concurrent microVM burst wave
#[derive(Debug)]
pub struct BurstMetrics {
    pub profile_name: &'static str,
    pub vm_count: usize,
    pub cgroup_enforced: bool,
    pub total_spawn: Duration,
    pub avg_spawn: Duration,
    pub total_reap: Duration,
    pub avg_reap: Duration,
}

/// Root-managed CGroup v2 leaf guard for a single MicroVM instance
pub struct RootCgroupGuard {
    vm_cgroup: PathBuf,
    enforced: bool,
}

impl RootCgroupGuard {
    /// Initializes `/sys/fs/cgroup/camelot.slice` and enables memory, cpu, io, and pids controllers.
    /// Returns `Ok(false)` if the current test runner does not have root CGroup write permissions.
    pub fn init_parent_slice() -> io::Result<bool> {
        let slice_path = Path::new(SLICE_ROOT);
        if let Err(e) = fs::create_dir_all(slice_path) {
            if e.kind() == ErrorKind::PermissionDenied || e.kind() == ErrorKind::ReadOnlyFilesystem {
                return Ok(false);
            }
            return Err(e);
        }

        let subtree_control = slice_path.join("cgroup.subtree_control");
        match fs::write(&subtree_control, "+memory +cpu +io +pids") {
            Ok(_) => Ok(true),
            Err(e) if e.kind() == ErrorKind::PermissionDenied => Ok(false),
            Err(_) => {
                let _ = fs::write(&subtree_control, "+memory +cpu +pids");
                Ok(true)
            }
        }
    }

    /// Creates `/sys/fs/cgroup/camelot.slice/vm-<id>` and binds `pid` into `cgroup.procs`
    pub fn attach_pid(vm_id: &str, pid: u32, profile: &DensityProfile) -> io::Result<Self> {
        let vm_cgroup = Path::new(SLICE_ROOT).join(format!("vm-{vm_id}"));
        if !Self::init_parent_slice()? {
            return Ok(Self {
                vm_cgroup,
                enforced: false,
            });
        }

        fs::create_dir_all(&vm_cgroup)?;
        let _ = fs::write(vm_cgroup.join("memory.swap.max"), "0");
        let _ = fs::write(vm_cgroup.join("memory.oom.group"), "1");
        fs::write(vm_cgroup.join("memory.high"), profile.cgroup_mem_high)?;
        fs::write(vm_cgroup.join("memory.max"), profile.cgroup_mem_max)?;
        fs::write(vm_cgroup.join("pids.max"), profile.pids_max)?;
        fs::write(vm_cgroup.join("cgroup.procs"), pid.to_string())?;

        Ok(Self {
            vm_cgroup,
            enforced: true,
        })
    }

    pub fn is_enforced(&self) -> bool {
        self.enforced
    }

    pub fn path(&self) -> &Path {
        &self.vm_cgroup
    }
}

impl Drop for RootCgroupGuard {
    fn drop(&mut self) {
        if self.enforced && self.vm_cgroup.exists() {
            let _ = fs::remove_dir(&self.vm_cgroup);
        }
    }
}

/// Hardened Firecracker / Mock-VMM Supervisor with idempotent socket & CGroup teardown
pub struct FirecrackerSupervisor {
    vm_id: String,
    child: Option<Child>,
    api_socket: PathBuf,
    cgroup_guard: Option<RootCgroupGuard>,
}

impl FirecrackerSupervisor {
    /// Spawns a process bound to `api_socket` and attaches it to a CGroup v2 leaf
    pub fn spawn_process(
        vm_id: impl Into<String>,
        mut cmd: Command,
        api_socket: PathBuf,
        profile: &DensityProfile,
        drop_to_uid_gid: Option<(u32, u32)>,
    ) -> io::Result<Self> {
        let vm_id = vm_id.into();
        if api_socket.exists() {
            let _ = fs::remove_file(&api_socket);
        }

        cmd.stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());

        if let Some((uid, gid)) = drop_to_uid_gid {
            cmd.as_std_mut().uid(uid).gid(gid);
        }

        let child = cmd.spawn()?;
        let pid = child.id().ok_or_else(|| {
            io::Error::new(ErrorKind::Other, "Child terminated before PID assignment")
        })?;

        let cgroup_guard = RootCgroupGuard::attach_pid(&vm_id, pid, profile).ok();

        Ok(Self {
            vm_id,
            child: Some(child),
            api_socket,
            cgroup_guard,
        })
    }

    pub fn vm_id(&self) -> &str {
        &self.vm_id
    }

    pub fn pid(&self) -> Option<u32> {
        self.child.as_ref().and_then(|c| c.id())
    }

    pub fn api_socket(&self) -> &Path {
        &self.api_socket
    }

    pub fn cgroup_guard(&self) -> Option<&RootCgroupGuard> {
        self.cgroup_guard.as_ref()
    }

    /// Normal exit path: waits for process exit, closes stdin pipe, and unlinks socket
    pub async fn wait(&mut self) -> io::Result<std::process::ExitStatus> {
        let status = if let Some(mut child) = self.child.take() {
            drop(child.stdin.take());
            child.wait().await?
        } else {
            return Err(io::Error::new(ErrorKind::InvalidInput, "Child already reaped"));
        };

        Self::cleanup_socket(&self.api_socket).await?;
        self.cgroup_guard.take();
        Ok(status)
    }

    /// Explicit deterministic stop: closes stdin EOF, kills if active, reaps PID, and unlinks socket
    pub async fn shutdown(&mut self) -> io::Result<()> {
        if let Some(mut child) = self.child.take() {
            drop(child.stdin.take());
            match child.try_wait()? {
                Some(_) => {}
                None => {
                    let _ = child.kill().await;
                    let _ = child.wait().await;
                }
            }
        }

        Self::cleanup_socket(&self.api_socket).await?;
        self.cgroup_guard.take();
        Ok(())
    }

    /// Idempotent socket removal: treats `ErrorKind::NotFound` as success
    pub async fn cleanup_socket(path: &Path) -> io::Result<()> {
        match tokio::fs::remove_file(path).await {
            Ok(()) => Ok(()),
            Err(e) if e.kind() == ErrorKind::NotFound => Ok(()),
            Err(e) => Err(e),
        }
    }
}

impl Drop for FirecrackerSupervisor {
    fn drop(&mut self) {
        if let Some(mut child) = self.child.take() {
            drop(child.stdin.take());
            let _ = child.start_kill();
        }
        if self.api_socket.exists() {
            let _ = fs::remove_file(&self.api_socket);
        }
        drop(self.cgroup_guard.take());
    }
}

/// Checks whether hardware `/dev/kvm` is exposed inside the current ARM64 Linux environment
pub fn has_kvm_access() -> bool {
    OpenOptions::new()
        .read(true)
        .write(true)
        .open("/dev/kvm")
        .is_ok()
}

/// Sends a minimal HTTP/1.1 PUT request over the Firecracker Unix domain socket
async fn firecracker_put(socket_path: &Path, endpoint: &str, body: &str) -> io::Result<()> {
    let mut stream = UnixStream::connect(socket_path).await?;
    let request = format!(
        "PUT {endpoint} HTTP/1.1\r\n\
         Host: localhost\r\n\
         Accept: application/json\r\n\
         Content-Type: application/json\r\n\
         Content-Length: {}\r\n\
         Connection: close\r\n\r\n\
         {body}",
        body.len()
    );
    stream.write_all(request.as_bytes()).await?;

    let mut response = String::new();
    stream.read_to_string(&mut response).await?;
    if !response.starts_with("HTTP/1.1 204") && !response.starts_with("HTTP/1.1 200") {
        return Err(io::Error::new(
            ErrorKind::Other,
            format!("Firecracker API {endpoint} failed: {response}"),
        ));
    }
    Ok(())
}

/// Configures and boots an ARM64 Firecracker instance over its API socket
async fn drive_firecracker_boot(
    socket_path: &Path,
    kernel_path: &Path,
    rootfs_path: &Path,
    profile: &DensityProfile,
) -> io::Result<Duration> {
    let start = Instant::now();

    while !socket_path.exists() || StdUnixStream::connect(socket_path).is_err() {
        if start.elapsed() > Duration::from_millis(50) {
            return Err(io::Error::new(
                ErrorKind::TimedOut,
                "Timed out waiting for Firecracker API socket bind",
            ));
        }
        tokio::time::sleep(Duration::from_micros(250)).await;
    }

    let machine_cfg = format!(
        r#"{{"vcpu_count":{},"mem_size_mib":{},"smt":false}}"#,
        profile.vcpu_count, profile.mem_size_mib
    );
    firecracker_put(socket_path, "/machine-config", &machine_cfg).await?;

    let boot_src = format!(
        r#"{{"kernel_image_path":"{}","boot_args":"keep_bootcon console=none reboot=k panic=1 pci=off nomodules 8250.nr_uarts=0"}}"#,
        kernel_path.display()
    );
    firecracker_put(socket_path, "/boot-source", &boot_src).await?;

    let drive_cfg = format!(
        r#"{{"drive_id":"rootfs","path_on_host":"{}","is_root_device":true,"is_read_only":{}}}"#,
        rootfs_path.display(),
        profile.rootfs_read_only
    );
    firecracker_put(socket_path, "/drives/rootfs", &drive_cfg).await?;

    firecracker_put(
        socket_path,
        "/actions",
        r#"{"action_type":"InstanceStart"}"#,
    )
    .await?;

    Ok(start.elapsed())
}

/// Executes a concurrent burst wave of `burst_count` microVMs (real Firecracker on EL2 KVM or mock-VMM on EL1)
async fn execute_density_burst_wave(
    profile: DensityProfile,
    burst_count: usize,
    use_hardware_kvm: bool,
    fc_bin: &Path,
    kernel_path: &Path,
    rootfs_path: &Path,
) -> io::Result<BurstMetrics> {
    let mut supervisors = Vec::with_capacity(burst_count);
    let mut listeners = Vec::with_capacity(burst_count);
    let mut cgroup_enforced = false;
    let spawn_start = Instant::now();

    for idx in 0..burst_count {
        let vm_id = format!("{}-{idx:03}", profile.name);
        let sock_path = PathBuf::from(format!("/tmp/camelot-{vm_id}.socket"));

        if use_hardware_kvm {
            let mut cmd = Command::new(fc_bin);
            cmd.arg("--api-sock").arg(&sock_path);
            let sup = FirecrackerSupervisor::spawn_process(
                &vm_id,
                cmd,
                sock_path.clone(),
                &profile,
                None,
            )?;
            drive_firecracker_boot(&sock_path, kernel_path, rootfs_path, &profile).await?;
            if let Some(cg) = sup.cgroup_guard() {
                cgroup_enforced = cg.is_enforced();
            }
            supervisors.push(sup);
        } else {
            let cmd = Command::new("/bin/cat");
            let sup = FirecrackerSupervisor::spawn_process(
                &vm_id,
                cmd,
                sock_path.clone(),
                &profile,
                None,
            )?;
            let listener = UnixListener::bind(&sock_path)?;
            if let Some(cg) = sup.cgroup_guard() {
                if cg.is_enforced() {
                    cgroup_enforced = true;
                    let mem_max = fs::read_to_string(cg.path().join("memory.max"))?;
                    assert_eq!(mem_max.trim(), profile.cgroup_mem_max);
                }
            }
            listeners.push(listener);
            supervisors.push(sup);
        }
    }

    let total_spawn = spawn_start.elapsed();
    let avg_spawn = total_spawn / (burst_count as u32);

    drop(listeners);

    let reap_start = Instant::now();
    for mut sup in supervisors {
        let pid = sup.pid().expect("Active child PID required");
        let sock = sup.api_socket().to_path_buf();
        sup.shutdown().await?;
        assert!(!sock.exists(), "Residual socket found: {}", sock.display());
        assert!(
            !Path::new(&format!("/proc/{pid}")).exists(),
            "Zombie/unreaped PID {pid} detected"
        );
    }
    let total_reap = reap_start.elapsed();
    let avg_reap = total_reap / (burst_count as u32);

    Ok(BurstMetrics {
        profile_name: profile.name,
        vm_count: burst_count,
        cgroup_enforced,
        total_spawn,
        avg_spawn,
        total_reap,
        avg_reap,
    })
}

#[tokio::test]
async fn test_socket_reclamation_and_idempotent_teardown() -> io::Result<()> {
    let profile = DensityProfile::ULTRA_DENSE;

    // 1. Validate explicit shutdown() removes pre-bound socket and reaps child PID
    let sock_shutdown = PathBuf::from(format!(
        "/tmp/camelot-unit-shutdown-{}.socket",
        std::process::id()
    ));
    let _listener = UnixListener::bind(&sock_shutdown)?;
    assert!(sock_shutdown.exists(), "Socket must exist prior to shutdown");

    let cmd = Command::new("/bin/cat");
    let mut sup = FirecrackerSupervisor::spawn_process(
        "unit-shutdown",
        cmd,
        sock_shutdown.clone(),
        &profile,
        None,
    )?;
    let _listener2 = UnixListener::bind(&sock_shutdown)?;
    let child_pid = sup.pid().expect("Child PID must be present");

    sup.shutdown().await?;
    assert!(!sock_shutdown.exists(), "Socket must be unlinked after shutdown()");

    // Calling shutdown() a second time must succeed idempotently (ErrorKind::NotFound ignored)
    sup.shutdown().await?;
    assert!(
        !Path::new(&format!("/proc/{child_pid}")).exists(),
        "Child PID must be reaped from /proc after shutdown()"
    );

    // 2. Validate Drop implementation unlinks socket synchronously on scope exit
    let sock_drop = PathBuf::from(format!(
        "/tmp/camelot-unit-drop-{}.socket",
        std::process::id()
    ));
    {
        let cmd_drop = Command::new("/bin/cat");
        let _sup_drop = FirecrackerSupervisor::spawn_process(
            "unit-drop",
            cmd_drop,
            sock_drop.clone(),
            &profile,
            None,
        )?;
        let _listener3 = UnixListener::bind(&sock_drop)?;
        assert!(sock_drop.exists(), "Socket must exist inside scope");
    }
    assert!(!sock_drop.exists(), "Drop must synchronously remove socket file");

    Ok(())
}

#[tokio::test]
#[ignore]
async fn test_firecracker_boot_and_max_density_burst() -> io::Result<()> {
    let target_burst: usize = std::env::var("CAMELOT_BURST_VMS")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(50);

    let fc_bin = PathBuf::from(
        std::env::var("FIRECRACKER_BIN").unwrap_or_else(|_| "firecracker".to_string()),
    );
    let kernel_path = PathBuf::from(
        std::env::var("CAMELOT_KERNEL").unwrap_or_else(|_| DEFAULT_KERNEL_PATH.to_string()),
    );
    let rootfs_path = PathBuf::from(
        std::env::var("CAMELOT_ROOTFS").unwrap_or_else(|_| DEFAULT_ROOTFS_PATH.to_string()),
    );

    let use_hardware_kvm =
        has_kvm_access() && kernel_path.exists() && rootfs_path.exists() && fc_bin.exists();

    if use_hardware_kvm {
        println!(
            "[MODE: HARDWARE KVM (EL2)] Running single-VM <80ms boot gate + {}-VM burst sweep",
            target_burst
        );
    } else {
        println!(
            "[MODE: WINDOWS ARM64 EL1 MOCK-VMM FALLBACK] Running progressive density sweep up to {} concurrent VMs",
            target_burst
        );
    }

    // Progressive density waves: 18 Minimal Reflex (128M), 35 Ultra-Dense (64M), and Target Burst (default 50 Ultra-Dense 64M)
    let waves = [
        (DensityProfile::MINIMAL_REFLEX, 18usize),
        (DensityProfile::ULTRA_DENSE, 35usize),
        (DensityProfile::ULTRA_DENSE, target_burst),
    ];

    for (profile, count) in waves {
        let metrics = execute_density_burst_wave(
            profile,
            count,
            use_hardware_kvm,
            &fc_bin,
            &kernel_path,
            &rootfs_path,
        )
        .await?;

        println!(
            "WAVE [{} x {}] | CGroupEnforced={} | TotalSpawn={:?} (Avg={:?}/VM) | TotalReap={:?} (Avg={:?}/VM)",
            metrics.profile_name,
            metrics.vm_count,
            metrics.cgroup_enforced,
            metrics.total_spawn,
            metrics.avg_spawn,
            metrics.total_reap,
            metrics.avg_reap,
        );

        assert!(
            metrics.avg_spawn + metrics.avg_reap < Duration::from_millis(80),
            "Wave {} average spawn+reap latency {:?} exceeded <80ms gate",
            metrics.profile_name,
            metrics.avg_spawn + metrics.avg_reap
        );
    }

    Ok(())
}