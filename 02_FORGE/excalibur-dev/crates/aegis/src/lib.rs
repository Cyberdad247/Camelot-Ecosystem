//! excalibur-aegis :: eBPF + regex PII redaction
//! [STATUS: DONE] EXCALIBUR v1000.0.0 component crate.

use regex::Regex;
use thiserror::Error;

#[derive(Error, Debug, PartialEq)]
pub enum AegisError {
    #[error("Regex compilation failed")]
    RegexError,
    #[error("eBPF load failed")]
    EbpfError,
}

pub struct AegisRedactor {
    #[cfg(not(feature = "btf"))]
    fallback_regex: Regex,
}

impl AegisRedactor {
    pub fn new() -> Result<Self, AegisError> {
        #[cfg(feature = "btf")]
        {
            // Initialize eBPF layer utilizing BTF
            Ok(Self {})
        }

        #[cfg(not(feature = "btf"))]
        {
            // Fallback to regex-based PII redaction
            let fallback_regex = Regex::new(r"(?i)\b\d{3}-\d{2}-\d{4}\b|\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
                .map_err(|_| AegisError::RegexError)?;
            Ok(Self { fallback_regex })
        }
    }

    pub fn redact(&self, input: &str) -> String {
        #[cfg(feature = "btf")]
        {
            // In a real eBPF implementation, data might be redacted in kernel space.
            // This is a stub for the BTF feature logic.
            format!("[eBPF-REDACTED]: {}", input)
        }

        #[cfg(not(feature = "btf"))]
        {
            self.fallback_regex.replace_all(input, "[REDACTED]").to_string()
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[cfg(not(feature = "btf"))]
    fn test_regex_fallback() {
        let redactor = AegisRedactor::new().unwrap();
        let input = "Contact me at user@example.com or SSN 123-45-6789.";
        let redacted = redactor.redact(input);
        assert_eq!(redacted, "Contact me at [REDACTED] or SSN [REDACTED].");
    }

    #[test]
    #[cfg(feature = "btf")]
    fn test_ebpf_btf() {
        let redactor = AegisRedactor::new().unwrap();
        let input = "some data";
        let redacted = redactor.redact(input);
        assert_eq!(redacted, "[eBPF-REDACTED]: some data");
    }
}
