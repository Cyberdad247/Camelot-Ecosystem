// WebGPU Shader — Reactive Glass Cockpit 3D-to-2D Spatial Network
// Part of cartridge-hive-ide-swarm (/hive-core/telemetry/glass_cockpit.wgsl)
// Visualizes Zero-Copy memfd IPC traffic, AgentBus pulses, and VFS refractions in real-time.

struct Uniforms {
    u_resolution : vec2<f32>,
    u_time : f32,
    u_ram_utilization : f32,
    u_agent_count : f32,
    u_cow_delta : f32,
};

@group(0) @binding(0) var<uniform> uniforms : Uniforms;

struct VertexInput {
    @location(0) position : vec3<f32>,
    @location(1) uv : vec2<f32>,
    @location(2) normal : vec3<f32>,
};

struct VertexOutput {
    @builtin(position) clip_position : vec4<f32>,
    @location(0) uv : vec2<f32>,
    @location(1) world_pos : vec3<f32>,
};

@vertex
fn vs_main(in : VertexInput) -> VertexOutput {
    var out : VertexOutput;
    // 3D spatial projection into 2D cockpit plane
    let pulse = sin(uniforms.u_time * 2.5 + in.position.y * 3.0) * (uniforms.u_cow_delta * 0.5);
    let displaced = in.position + in.normal * pulse;
    
    out.clip_position = vec4<f32>(displaced.x, displaced.y, displaced.z, 1.0);
    out.uv = in.uv;
    out.world_pos = displaced;
    return out;
}

@fragment
fn fs_main(in : VertexOutput) -> @location(0) vec4<f32> {
    // Luxury Minimalist Brutalism Palette: Luxora Gold (#D4AF37), Obsidian Black, Cyan IPC Ribbons
    let luxora_gold = vec3<f32>(0.831, 0.686, 0.216);
    let obsidian = vec3<f32>(0.039, 0.039, 0.051);
    let ipc_cyan = vec3<f32>(0.150, 0.850, 0.950);
    let alert_red = vec3<f32>(0.920, 0.200, 0.200);

    let uv = in.uv;
    let dist_center = length(uv - vec2<f32>(0.5, 0.5));
    
    // Wave pulse representing Zero-Copy IPC traffic
    let wave = sin(dist_center * 30.0 - uniforms.u_time * 4.0);
    let wave_mask = smoothstep(0.85, 1.0, wave);

    // Dynamic color selection based on 8GB RAM utilization ceiling
    var base_color = mix(obsidian, luxora_gold, smoothstep(0.4, 0.0, dist_center));
    if (uniforms.u_ram_utilization > 0.85) {
        base_color = mix(base_color, alert_red, uniforms.u_ram_utilization);
    }

    // Blend in IPC ribbons
    let final_color = mix(base_color, ipc_cyan, wave_mask * 0.4);
    let alpha = clamp(1.0 - dist_center * 1.2, 0.15, 0.95);

    return vec4<f32>(final_color, alpha);
}
