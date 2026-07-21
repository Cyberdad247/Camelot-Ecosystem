# ==============================================================================
# DESIGN.md - THE SOVEREIGN COMPILER GENOME (v1000)
# ARCHETYPE: Hardened Terminal Cyberpunk & "Spaceship Instruction Manual"
# STACK: Next.js 14 + Tailwind v4 + Three.js (WebGPU) + Framer Motion
# ==============================================================================
design_tokens:
  colors:
    # 60-30-10 Rule enforced: 60% Backgrounds, 30% Canvas/Borders, 10% Accents
    background_void:
      $value: "#08080A"
      $description: "Deep Obsidian Void (Primary 60%)"
    canvas_slate:
      $value: "#0D0E12"
      $description: "Container Slate (Secondary Panels)"
    border_iron:
      $value: "#1A1D26"
      $description: "Iron Rim (Separators & Grid Lines)"
    accent_active:
      $value: "#00FFC2"
      $description: "Radiant Trit-Cyan (Primary CTA / 10% Rule)"
    accent_warning:
      $value: "#FF3B69"
      $description: "Scorpion Crimson (Destructive/Alert states)"
    text_system:
      $value: "#8E95A5"
      $description: "Lattice Grey (Secondary Body Text)"
    text_primary:
      $value: "#FFFFFF"
      $description: "Pure White for high-contrast H1/H2 headers"
  typography:
    font_families:
      primary:
        $value: "'JetBrains Mono', 'Fira Code', monospace"
        $description: "Technical authority, used for layout and data execution"
    scales:
      ratio:
        $value: "1.25"
        $description: "Major Third REM-based type scale"
    readability:
      line_width: "50-75ch"
      line_height: "1.5x"
      $description: "Optimized limits to prevent cognitive fatigue"
  spacing:
    rhythm:
      $value: "8pt"
      $description: "Strict 8-point mathematical grid (8, 16, 24, 32, 40...) for all margins and padding"
architecture_rules:
  layout_engine:
    grid_system:
      desktop: "12-column grid"
      tablet: "8-column grid"
      mobile: "4-column grid"
    patterns:
      - "Bento Grid Architecture: Data-dense, modular, rectangular cells for complex metrics"
      - "Barely There UI: Hyper-minimalist chrome allowing the data/3D canvas to be the primary focus"
      - "Vertical Chaos Elimination: Strict adherence to the C.R.A.P. framework (Contrast, Repetition, Alignment, Proximity)"
  interaction_physics:
    performance_constants:
      doherty_threshold: "< 400ms"
      max_load_time: "< 2.75s"
      $description: "Thresholds required to maintain addictive fluidity"
    animations:
      micro_interactions: "Framer Motion applied for state transitions (e.g., spring bounces, border glows on hover)"
      macro_interactions: "GSAP for scroll-triggered storytelling, tied directly to scroll progress (scrub: true)"
      streaming_ui: "Character-by-character text-generate effects to mask LLM latency"
  geo_agentic_readiness:
    algorithmic_trinity:
      understandability: "Strict semantic HTML5 hierarchy (H1 -> H2 -> H3) enabling 'Chunk-Level Retrieval' by AI agents"
      credibility: "Human-in-the-Loop trust signals, E-E-A-T verification markers"
      deliverability: "JSON-LD schema markup baked into the metadata layer; machine-readable APIs"
  core_components:
    SovereignEnclaveShell:
      layout: "Full-viewport responsive dashboard shell with a left-hand navigation array mapping the 5 core architectural layers of Camelot-OS"
      top_bar: "Fixed [TELEMETRY_HUD] displaying animated, state-driven metrics: [CPU: 100%] [RAM: 4.1GB/8.0GB] [LATTICE: ACTIVE] [MTP: COHERENT]"
    ManifoldMatrixMonitor:
      layout: "Center-pane Bento grid visualizer mapping active system tasks onto a 25-Dimensional manifold"
      nodes: "5x5 structural coordinate field representing the active Knight cluster. Nodes display live tooltip tags when hovered (e.g., Merlin Ω [ORCHESTRATOR], Sir Boris [EXECUTOR], Sir Alex [PLANNER], Sir Sentinel [SECURITY], Lady Apis [RESEARCH], Lady Mnemosyne [ARCHIVIST], Sir Forge [EXECUTION])"
