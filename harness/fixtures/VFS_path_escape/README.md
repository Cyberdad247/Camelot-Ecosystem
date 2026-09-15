# Fixture: VFS_path_escape

Workload attempts to write outside its approved workspace root (parent-path
escape such as `../`, absolute path, or symlink jump). The VFS Guardian
preflight must deny before any write reaches disk.

Verify: `VFS_path_escape_denied` fires; write path rejected; no file created
outside `worktree/`; protected paths (`protected_write_denied`) also denied
(§14.1, §14.3).
