// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
package main

import (
	"fmt"
	"os/exec"
	"strconv"
	"strings"
	"time"
)

// Omega_AEGIS_HEARTBEAT v2.2 [KINETIC_CORRECTED]
// Implementation of the Autonomous Watchtower S.I.T. Loop.
// Updated with correct binary flags and PowerShell hooks.

const (
	FastBeatInterval = 5 * time.Minute
	SlowBeatInterval = 4 * time.Hour

	RotelPath = `C:\Users\vizio\CAMELOT_OS\02_FORGE\kinetic\rotel\target\release\rotel.exe`
	CriboPath = `C:\Users\vizio\CAMELOT_OS\02_FORGE\kinetic\cribo\target\release\cribo.exe`
	MapPath   = `docs\EMPIRE_MAP.md`
)

func logTelemetry(name string, status string, details string) {
	// ⚡ Sir Kronos: Rotel Telemetry Injection
	attrs := fmt.Sprintf(`{"status":"%s","details":"%s"}`, status, details)
	cmd := exec.Command(RotelPath, "log", "--name", name, "--attrs", attrs)
	if out, err := cmd.CombinedOutput(); err != nil {
		fmt.Printf("⚠️ [KRONOS]: Telemetry failed: %v (%s)\n", err, string(out))
	} else {
		fmt.Printf("📊 [KRONOS]: Telemetry Logged (%s)\n", name)
	}
}

func checkResources() {
	// Kinetic Sense via PowerShell (No external deps)
	cmd := exec.Command("powershell", "-Command", "Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty FreePhysicalMemory")
	out, err := cmd.CombinedOutput()
	if err != nil {
		logTelemetry("RESOURCE_CHECK", "ERROR", err.Error())
		return
	}

	kbFreeStr := strings.TrimSpace(string(out))
	kbFree, _ := strconv.Atoi(kbFreeStr)
	gbFree := float64(kbFree) / 1024 / 1024

	fmt.Printf("🧠 [RAM]: %.2f GB Free\n", gbFree)

	if gbFree < 8.0 {
		fmt.Println("🚨 [AEGIS]: MEMORY CRITICAL (<8GB)!")
		logTelemetry("RESOURCE_ALERT", "CRITICAL", fmt.Sprintf("%.2f GB Free", gbFree))
		// Trigger Triage (e.g., clear temp)
	} else {
		logTelemetry("RESOURCE_HEARTBEAT", "NOMINAL", fmt.Sprintf("%.2f GB Free", gbFree))
	}
}

func FastBeat() {
	fmt.Printf("\n[PULSE]: FAST BEAT %v\n", time.Now().Format("15:04:05"))

	// 1. Sir Kronos (Metrics)
	checkResources()

	// 2. Sir Sentinel (Integrity)
	// Using --entry as verified in help
	fmt.Println("🛡️ [SENTINEL]: Verifying Empire Map...")
	cCmd := exec.Command(CriboPath, "--entry", MapPath)
	if out, err := cCmd.CombinedOutput(); err != nil {
		fmt.Printf("⚠️ [SENTINEL]: Drift Detected or File Missing! %v\n", err)
		logTelemetry("INTEGRITY_CHECK", "FAIL", string(out))
	} else {
		fmt.Println("✅ [SENTINEL]: Empire Map Validated.")
		logTelemetry("INTEGRITY_CHECK", "PASS", "Map Verified")
	}
}

func SlowBeat() {
	fmt.Printf("\n[PULSE]: SLOW BEAT %v\n", time.Now().Format("15:04:05"))

	// 3. Deep Scan (Trivy)
	fmt.Println("🛡️ [SENTINEL]: Deep Vulnerability Scan...")
	tCmd := exec.Command("trivy", "fs", "--scanners", "vuln,secret", ".")
	if _, err := tCmd.CombinedOutput(); err != nil {
		fmt.Println("⚠️ [SENTINEL]: Trivy not found or failed.")
	} else {
		fmt.Println("✅ [SENTINEL]: Security Scan Complete.")
	}
}

func main() {
	fmt.Println("[WAR_ROOM]: Aegis Eternal Heartbeat v2.2 Initialized.")
	fmt.Println("[STATUS]: Background Daemon Running.")

	fastTicker := time.NewTicker(FastBeatInterval)
	slowTicker := time.NewTicker(SlowBeatInterval)

	FastBeat() // Immediate start

	for {
		select {
		case <-fastTicker.C:
			FastBeat()
		case <-slowTicker.C:
			SlowBeat()
		}
	}
}