//! Output Truncation Trap & Stream Limiter (Assimilated from Compiler Explorer)
//! =========================================================================
//!
//! Enforces:
//!   - Hard byte truncation cap on stdout/stderr (e.g. 100 KB default)
//!   - Maximum line count cap (e.g. 5,000 lines)
//!   - Automatic apoptosis / kill signal (`KillReason::OutputLimitExceeded`)
//!   - Retains diagnostic headers and prefixes while dropping unbounded spam

use serde::{Deserialize, Serialize};

pub const DEFAULT_MAX_OUTPUT_BYTES: usize = 100 * 1024; // 100 KB (Godbolt Compiler Explorer parity)
pub const DEFAULT_MAX_LINES: usize = 5000;
pub const TRUNCATION_NOTICE: &str = "\n<-- [Compiler Explorer Trap]: Output truncated (limit exceeded) -->\n";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutputTrapConfig {
    pub max_bytes: usize,
    pub max_lines: usize,
}

impl Default for OutputTrapConfig {
    fn default() -> Self {
        Self {
            max_bytes: DEFAULT_MAX_OUTPUT_BYTES,
            max_lines: DEFAULT_MAX_LINES,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct TruncatedStream {
    pub text: String,
    pub total_bytes_seen: usize,
    pub total_lines_seen: usize,
    pub is_truncated: bool,
}

#[derive(Debug)]
struct StreamBuffer {
    buffer: Vec<u8>,
    bytes_seen: usize,
    lines_seen: usize,
    truncated: bool,
}

impl StreamBuffer {
    fn new() -> Self {
        Self {
            buffer: Vec::new(),
            bytes_seen: 0,
            lines_seen: 0,
            truncated: false,
        }
    }

    fn append(&mut self, chunk: &[u8], max_bytes: usize, max_lines: usize) -> bool {
        self.bytes_seen += chunk.len();
        self.lines_seen += chunk.iter().filter(|&&b| b == b'\n').count();

        if self.truncated {
            return false;
        }

        if self.bytes_seen > max_bytes || self.lines_seen > max_lines {
            self.truncated = true;
            // Retain up to max_bytes allowed from prior buffer + chunk
            let available_space = max_bytes.saturating_sub(self.buffer.len());
            if available_space > 0 {
                let take_len = chunk.len().min(available_space);
                self.buffer.extend_from_slice(&chunk[..take_len]);
            }
            self.buffer.extend_from_slice(TRUNCATION_NOTICE.as_bytes());
            return true; // Just crossed threshold
        }

        self.buffer.extend_from_slice(chunk);
        false
    }

    fn finish(&self) -> TruncatedStream {
        TruncatedStream {
            text: String::from_utf8_lossy(&self.buffer).to_string(),
            total_bytes_seen: self.bytes_seen,
            total_lines_seen: self.lines_seen,
            is_truncated: self.truncated,
        }
    }
}

pub struct OutputTrap {
    config: OutputTrapConfig,
    stdout: StreamBuffer,
    stderr: StreamBuffer,
}

impl OutputTrap {
    pub fn new(config: OutputTrapConfig) -> Self {
        Self {
            config,
            stdout: StreamBuffer::new(),
            stderr: StreamBuffer::new(),
        }
    }

    /// Appends a chunk to stdout. Returns true if the output limit was just breached.
    pub fn append_stdout(&mut self, chunk: &[u8]) -> bool {
        self.stdout.append(chunk, self.config.max_bytes, self.config.max_lines)
    }

    /// Appends a chunk to stderr. Returns true if the output limit was just breached.
    pub fn append_stderr(&mut self, chunk: &[u8]) -> bool {
        self.stderr.append(chunk, self.config.max_bytes, self.config.max_lines)
    }

    pub fn is_limit_exceeded(&self) -> bool {
        self.stdout.truncated || self.stderr.truncated
    }

    pub fn finish_stdout(&self) -> TruncatedStream {
        self.stdout.finish()
    }

    pub fn finish_stderr(&self) -> TruncatedStream {
        self.stderr.finish()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn small_output_not_truncated() {
        let mut trap = OutputTrap::new(OutputTrapConfig {
            max_bytes: 1024,
            max_lines: 50,
        });

        let breached = trap.append_stdout(b"mov eax, 1\nret\n");
        assert!(!breached);
        assert!(!trap.is_limit_exceeded());

        let res = trap.finish_stdout();
        assert_eq!(res.text, "mov eax, 1\nret\n");
        assert_eq!(res.total_bytes_seen, 15);
        assert_eq!(res.total_lines_seen, 2);
        assert!(!res.is_truncated);
    }

    #[test]
    fn byte_limit_exceeded_triggers_truncation_notice() {
        let mut trap = OutputTrap::new(OutputTrapConfig {
            max_bytes: 30,
            max_lines: 100,
        });

        // 20 bytes
        let b1 = trap.append_stdout(b"12345678901234567890");
        assert!(!b1);
        assert!(!trap.is_limit_exceeded());

        // 20 more bytes -> total 40 > 30 -> triggers truncation
        let b2 = trap.append_stdout(b"abcdefghijklmnopqrst");
        assert!(b2);
        assert!(trap.is_limit_exceeded());

        let res = trap.finish_stdout();
        assert!(res.is_truncated);
        assert_eq!(res.total_bytes_seen, 40);
        assert!(res.text.contains("[Compiler Explorer Trap]"));
    }

    #[test]
    fn line_limit_exceeded_triggers_truncation() {
        let mut trap = OutputTrap::new(OutputTrapConfig {
            max_bytes: 10_000,
            max_lines: 3,
        });

        let chunk = b"line 1\nline 2\nline 3\nline 4\n";
        let breached = trap.append_stderr(chunk);
        assert!(breached);
        assert!(trap.is_limit_exceeded());

        let res = trap.finish_stderr();
        assert!(res.is_truncated);
        assert_eq!(res.total_lines_seen, 4);
        assert!(res.text.contains("[Compiler Explorer Trap]"));
    }
}
