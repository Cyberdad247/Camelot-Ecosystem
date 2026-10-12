//! Pure HATEOAS / HTMX Fragment Generator
//! ========================================

use serde::Serialize;

#[derive(Debug, Clone, Serialize)]
pub struct KnightTelemetryView {
    pub name: String,
    pub status: String,
    pub ram_mb: usize,
    pub role: String,
}

pub struct HateoasBuilder;

impl HateoasBuilder {
    /// Renders a pure hypermedia status card for HTMX swapping.
    pub fn render_knight_card(view: &KnightTelemetryView) -> String {
        format!(
            r##"<div class="knight-card border border-neutral-800 bg-neutral-900/60 p-4 rounded-lg">
  <div class="flex items-center justify-between">
    <h3 class="text-sm font-semibold text-[#D4AF37]">{name}</h3>
    <span class="text-xs px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">{status}</span>
  </div>
  <p class="text-xs text-neutral-400 mt-1">Role: {role}</p>
  <p class="text-xs font-mono text-neutral-500 mt-2">RAM: {ram_mb} MB / 4096 MB</p>
  <button hx-get="/api/knights/{name}/inspect" hx-target="#inspection-panel" hx-swap="innerHTML" class="mt-3 text-xs bg-neutral-800 hover:bg-neutral-700 text-white px-2 py-1 rounded">Inspect</button>
</div>"##,
            name = html_escape(&view.name),
            status = html_escape(&view.status),
            role = html_escape(&view.role),
            ram_mb = view.ram_mb,
        )
    }
}

fn html_escape(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#39;")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn render_card_contains_htmx_attributes() {
        let view = KnightTelemetryView {
            name: "SIR_HELIOS".into(),
            status: "ONLINE".into(),
            ram_mb: 512,
            role: "Sovereign Sentinel".into(),
        };

        let html = HateoasBuilder::render_knight_card(&view);
        assert!(html.contains("hx-get=\"/api/knights/SIR_HELIOS/inspect\""));
        assert!(html.contains("hx-target=\"#inspection-panel\""));
        assert!(html.contains("#D4AF37"));
        assert!(html.contains("512 MB / 4096 MB"));
    }
}
