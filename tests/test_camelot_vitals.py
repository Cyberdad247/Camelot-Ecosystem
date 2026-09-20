# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import pytest
from control_plane.infra.camelot_vitals import CamelotVitalsCollector, MetricSample


def test_camelot_vitals_collection_and_prometheus_export():
    collector = CamelotVitalsCollector(node_id="vps_cybertronia")
    
    samples = collector.collect_metrics(
        vps_memory_used_mb=5120.0,
        s26_memory_used_mb=280.0,
        psi_pressure_ratio=0.12,
        active_leases_count=18,
        aoede_voice_latency_ms=32.0,
        bifrost_ops_per_sec=24000.0
    )
    
    assert len(samples) == 6
    
    # Verify text export
    text = collector.export_prometheus_text(samples)
    assert "# HELP camelot_node_memory_bytes" in text
    assert "# TYPE camelot_node_memory_bytes gauge" in text
    assert 'camelot_node_memory_bytes{node="vps_hub",slice="systemd_root"} 5368709120.0' in text
    assert 'camelot_aoede_voice_latency_ms{pipeline="s2s_opus_wasm"} 32.0' in text
    assert 'camelot_bifrost_packet_throughput_ops{engine="9router"} 24000.0' in text


def test_camelot_vitals_alerting():
    collector = CamelotVitalsCollector(node_id="vps_cybertronia")
    
    # 1. Normal state (No alerts)
    alerts_normal = collector.evaluate_health_alerts(
        vps_memory_used_mb=4500.0,
        psi_pressure_ratio=0.08,
        aoede_voice_latency_ms=35.0
    )
    assert len(alerts_normal) == 0
    
    # 2. Critical Memory Alert (>7.2GB)
    alerts_critical = collector.evaluate_health_alerts(
        vps_memory_used_mb=7300.0,
        psi_pressure_ratio=0.92,
        aoede_voice_latency_ms=40.0
    )
    assert len(alerts_critical) == 1
    assert alerts_critical[0].severity == "CRITICAL"
    assert alerts_critical[0].alert_type == "MEMORY_PRESSURE_EXCEEDED"
    
    # 3. Audio Latency Spike Alert (>100ms)
    alerts_lat = collector.evaluate_health_alerts(
        vps_memory_used_mb=4500.0,
        psi_pressure_ratio=0.08,
        aoede_voice_latency_ms=145.0
    )
    assert len(alerts_lat) == 1
    assert alerts_lat[0].severity == "WARNING"
    assert alerts_lat[0].alert_type == "VOICE_LATENCY_DEGRADED"
