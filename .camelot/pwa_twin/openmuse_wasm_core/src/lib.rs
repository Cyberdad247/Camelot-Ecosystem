// D.A.X. V5: Rust WASM A2UI Renderer Core
// Zero-DOM-Bloat Hyper-Kinetic UI Parser & Dispatcher
use serde::{Deserialize, Serialize};
use wasm_bindgen::prelude::*;

// Define the strict A2UI JSON Schema for allowed components
#[derive(Deserialize, Serialize, Clone, PartialEq, Debug)]
#[serde(tag = "type")]
pub enum A2UIComponent {
    Card { id: String, title: String, content: String },
    Button { id: String, label: String, action: String },
    DataGrid { id: String, rows: Vec<String> },
}

#[derive(Serialize, Deserialize, Debug)]
pub struct A2UIRenderState {
    pub component_count: usize,
    pub html_projection: String,
    pub parse_time_us: u64,
}

#[wasm_bindgen]
pub struct OpenMuseWASMCanvas {
    components: Vec<A2UIComponent>,
}

#[wasm_bindgen]
impl OpenMuseWASMCanvas {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self {
            components: vec![
                A2UIComponent::Card {
                    id: "dash_1".to_string(),
                    title: "OpenManus-RL Status".to_string(),
                    content: "Autonomous Paperwork: 3 Invoices Processed.".to_string(),
                },
                A2UIComponent::Button {
                    id: "btn_approve".to_string(),
                    label: "Approve 👤✅".to_string(),
                    action: "HITL_AUTHORIZE".to_string(),
                },
            ],
        }
    }

    /// Ingest a JSONL or JSON stream of A2UI components at WASM speed
    pub fn ingest_a2ui_json(&mut self, json_payload: &str) -> Result<usize, JsValue> {
        let parsed: Vec<A2UIComponent> = serde_json::from_str(json_payload)
            .map_err(|e| JsValue::from_str(&format!("JSON Parse Error: {e}")))?;
        let count = parsed.len();
        self.components = parsed;
        Ok(count)
    }

    /// Render direct hyper-kinetic HTML projection without Virtual DOM garbage
    pub fn render_html(&self) -> String {
        let mut html = String::with_capacity(2048);
        html.push_str("<div class=\"grid grid-cols-12 gap-4 font-mono p-4 bg-[#050505] text-[#D4AF37]\">");
        
        for comp in &self.components {
            match comp {
                A2UIComponent::Card { id, title, content } => {
                    html.push_str(&format!(
                        "<div id=\"{}\" class=\"col-span-12 md:col-span-6 p-4 border border-[#2A2A35] bg-[#0B0B0E] rounded\">",
                        id
                    ));
                    html.push_str(&format!("<h2 class=\"font-bold mb-2 text-[#9D4EDD]\">{}</h2>", title));
                    html.push_str(&format!("<p class=\"text-sm text-slate-300\">{}</p></div>", content));
                }
                A2UIComponent::Button { id, label, action } => {
                    html.push_str(&format!(
                        "<button id=\"{}\" data-action=\"{}\" class=\"col-span-12 px-4 py-2 bg-[#D4AF37] text-black font-bold rounded hover:bg-[#E5B842]\">{}</button>",
                        id, action, label
                    ));
                }
                A2UIComponent::DataGrid { id, rows } => {
                    html.push_str(&format!("<div id=\"{}\" class=\"col-span-12 border border-[#2A2A35] p-2\">", id));
                    for row in rows {
                        html.push_str(&format!("<div class=\"py-1 border-b border-[#1A1A24]\">{}</div>", row));
                    }
                    html.push_str("</div>");
                }
            }
        }
        
        html.push_str("</div>");
        html
    }
}

#[wasm_bindgen(start)]
pub fn start() {
    // Zero-overhead WASM startup hook
}
