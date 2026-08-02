use crate::Result;
use serde_json::Value;
use std::collections::HashMap;

/// Sync handler signature. Tool handlers receive parsed params and return either a
/// structured result or a Protocol error. Async handlers are intentionally not in scope
/// for the additive scaffold — wire them at the Phase 1 cut window.
pub type ToolHandler = Box<dyn Fn(Value) -> Result<Value> + Send + Sync>;

pub struct Server {
    pub name: String,
    pub version: String,
    tools: HashMap<String, ToolHandler>,
}

impl Server {
    pub fn new(name: impl Into<String>, version: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            version: version.into(),
            tools: HashMap::new(),
        }
    }

    pub fn register_tool<F>(&mut self, name: impl Into<String>, handler: F)
    where
        F: Fn(Value) -> Result<Value> + Send + Sync + 'static,
    {
        self.tools.insert(name.into(), Box::new(handler));
    }

    pub fn list_tools(&self) -> Vec<String> {
        let mut out: Vec<String> = self.tools.keys().cloned().collect();
        out.sort();
        out
    }

    /// Dispatch a JSON-RPC `method` invocation against the registered tools.
    /// Unregistered methods yield a `MethodNotFound` protocol error (per JSON-RPC 2.0).
    pub fn dispatch(&self, method: &str, params: Value) -> Result<Value> {
        match self.tools.get(method) {
            Some(handler) => handler(params),
            None => Err(crate::PmcpError::Protocol {
                code: crate::types::ErrorCode::MethodNotFound,
                message: format!("tool not registered: {method}"),
            }),
        }
    }
}
