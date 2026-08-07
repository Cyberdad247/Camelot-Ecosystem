//! camelot-node-agent library surface — exposed so integration tests (and a
//! future gateway-side dispatcher) can exercise validation and compute
//! without going over HTTP.

pub mod backend;
pub mod compute;
pub mod http;
pub mod validate;
