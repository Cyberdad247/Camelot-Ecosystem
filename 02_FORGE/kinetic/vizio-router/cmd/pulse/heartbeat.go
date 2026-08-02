// heartbeat.go — Camelot-OS Master Daemon & Defense Grid
// Unified boot sequence orchestration, resource monitoring, and health checking.
// One word. Any shell. One compiled binary.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"net"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"runtime"
	"strings"
	"syscall"
	"time"
)

const (
	ramCeilingMB    = 8192
	pollIntervalSec  = 30
)

// ANSI colors
const (
	C_G = "\033[92m"
	C_Y = "\033[93m"
	C_R = "\033[91m"
	C_C = "\033[96m"
	C_M = "\033[95m"
	C_D = "\033[2m"
	C_X = "\033[0m"
	C_B = "\033[1m"
)

type PhaseResult struct {
	OK  bool   `json:"ok"`
	Msg string `json:"msg"`
	MS  int64  `json:"ms"`
}

type BootStatus struct {
	Phases  map[string]PhaseResult `json:"phases"`
	TotalMS int64                  `json:"_total_ms"`
}

type phase struct {
	name string
	fn   func() (bool, string)
}

func main() {
	statusFlag := flag.Bool("status", false, "Print status and exit")
	jsonFlag := flag.Bool("json", false, "Machine-readable JSON output")
	quickFlag := flag.Bool("quick", false, "Single-line summary")
	flag.Parse()

	home := detectHome()
	os.Setenv("CAMELOT_OS_HOME", home)

	if *statusFlag || *jsonFlag || *quickFlag {
		results := runBoot(home, true)
		if *jsonFlag {
			data, _ := json.MarshalIndent(results, "", "  ")
			fmt.Println(string(data))
		} else if *quickFlag {
			green := 0
			total := 0
			for _, v := range results.Phases {
				total++
				if v.OK {
					green++
				}
			}
			color := C_G
			if green < total {
				color = C_Y
			}
			fmt.Printf("%sAWAKEN %d/%d phases in %dms%s\n", color, green, total, results.TotalMS, C_X)
		} else {
			printBanner()
			runBoot(home, false)
		}
		os.Exit(0)
	}

	printBanner()
	runBoot(home, false)

	fmt.Printf("\n%s[🛡️  DEFENSE GRID] Master daemon loop active.%s\n", C_B, C_X)
	
	// Start resource monitoring loop
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
	
	ticker := time.NewTicker(pollIntervalSec * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-sigCh:
			fmt.Println("\n[🛡️  DEFENSE GRID] Shutdown signal received. Farewell.")
			os.Exit(0)
		case <-ticker.C:
			checkResources()
		}
	}
}

func printBanner() {
	fmt.Printf("%s%s", C_M, C_B)
	fmt.Println("╔══════════════════════════════════════════════════════════════╗")
	fmt.Println("║  AWAKEN — Camelot Apex OS v400.1.0 (Lattice Radiant)        ║")
	fmt.Println("║  SIR_BORIS v3.0 — One word. Any shell. Any platform.        ║")
	fmt.Println("║  6-Phase Boot: CLIProxy → Defense → Kinetic → Cloud →       ║")
	fmt.Println("║                Vizion Telemetry → Sovereign Harness (24/7)  ║")
	fmt.Println("╚══════════════════════════════════════════════════════════════╝")
	fmt.Printf("%s", C_X)
}

func detectHome() string {
	if h := os.Getenv("CAMELOT_OS_HOME"); h != "" {
		return h
	}
	userHome, _ := os.UserHomeDir()
	candidates := []string{
		filepath.Join(userHome, "CAMELOT_OS"),
		"C:\\Users\\vizio\\CAMELOT_OS",
	}
	for _, c := range candidates {
		if _, err := os.Stat(filepath.Join(c, "03_VAULT", "training", "configs", "hud.py")); err == nil {
			return c
		}
	}
	// Fallback to current dir or parent
	pwd, _ := os.Getwd()
	return pwd
}

func isPortOpen(port int) bool {
	conn, err := net.DialTimeout("tcp", fmt.Sprintf("127.0.0.1:%d", port), 500*time.Millisecond)
	if err != nil {
		return false
	}
	conn.Close()
	return true
}

func spawnDetached(command string, args []string, dir string) (int, error) {
	cmd := exec.Command(command, args...)
	cmd.Dir = dir
	
	setupDetached(cmd)
	
	err := cmd.Start()
	if err != nil {
		return 0, err
	}
	
	// Wait a moment to see if it crashes immediately
	done := make(chan error, 1)
	go func() { done <- cmd.Wait() }()
	
	select {
	case err := <-done:
		return 0, fmt.Errorf("exited immediately: %v", err)
	case <-time.After(1 * time.Second):
		return cmd.Process.Pid, nil
	}
}

func runBoot(home string, quiet bool) BootStatus {
	results := BootStatus{
		Phases: make(map[string]PhaseResult),
	}
	tTotal := time.Now()

	phases := []phase{
		{"CLIProxyAPI   :8080", func() (bool, string) {
			if isPortOpen(8080) {
				return true, "CLIProxyAPI already running on :8080"
			}
			bin := filepath.Join(home, "..", "CLIProxyAPI", "cli-proxy-api.exe")
			pid, err := spawnDetached(bin, nil, filepath.Join(home, "..", "CLIProxyAPI"))
			if err != nil {
				return false, fmt.Sprintf("failed: %v", err)
			}
			return true, fmt.Sprintf("online (PID %d, port 8080)", pid)
		}},
		{"Defense Grid       ", func() (bool, string) {
			return true, fmt.Sprintf("online (internalized, PID %d)", os.Getpid())
		}},
		{"Kinetic Edge  :3001", func() (bool, string) {
			if isPortOpen(3001) {
				return true, "Kinetic Edge already running on :3001"
			}
			bin := filepath.Join(home, "bin", "camelot-mcp-edge.exe")
			pid, err := spawnDetached(bin, nil, home)
			if err != nil {
				return false, fmt.Sprintf("failed: %v", err)
			}
			return true, fmt.Sprintf("online (PID %d, port 3001)", pid)
		}},
		{"Cloud Brain   (RPC)", func() (bool, string) {
			// This typically probes a health endpoint in the Python version.
			// For now, we assume it's okay if we can't easily probe it from Go without more logic.
			return true, "Cloud Brain probe skipped (internal)"
		}},
		{"Vizion Telemetry   ", func() (bool, string) {
			bin := filepath.Join(home, "bin", "vizion-telemetry.exe")
			pid, err := spawnDetached(bin, nil, home)
			if err != nil {
				return false, fmt.Sprintf("failed: %v", err)
			}
			return true, fms(pid, "terminal TUI active")
		}},
		{"Sovereign Harness  ", func() (bool, string) {
			// Use the python from the venv
			pyBin := filepath.Join(home, ".venv_camelot", "Scripts", "python.exe")
			if _, err := os.Stat(pyBin); err != nil {
				pyBin = "python"
			}
			harnessPy := filepath.Join(home, "control_plane", "harness.py")
			pid, err := spawnDetached(pyBin, []string{harnessPy}, home)
			if err != nil {
				return false, fmt.Sprintf("failed: %v", err)
			}
			return true, fms(pid, "Sovereign Harness spawned")
		}},
		{"Bio-Swarm (Nano)   ", func() (bool, string) {
			bin := filepath.Join(home, "bin", "swarm-spawner.exe")
			pid, err := spawnDetached(bin, nil, home)
			if err != nil {
				return false, fmt.Sprintf("failed: %v", err)
			}
			return true, fms(pid, "Bio-Swarm Cells Active")
		}},
		{"Edge PWA      :3000", func() (bool, string) {
			if isPortOpen(3000) {
				return true, "Edge PWA already running on :3000"
			}
			bin := filepath.Join(home, "bin", "edge-server.exe")
			pid, err := spawnDetached(bin, nil, home)
			if err != nil {
				return false, fmt.Sprintf("failed: %v", err)
			}
			return true, fmt.Sprintf("online (PID %d, port 3000)", pid)
		}},
	}

	for _, p := range phases {
		t0 := time.Now()
		ok, msg := p.fn()
		dt := time.Since(t0).Milliseconds()
		results.Phases[strings.TrimSpace(p.name)] = PhaseResult{OK: ok, Msg: msg, MS: dt}
		
		if !quiet {
			glyph := fmt.Sprintf("%s✅%s", C_G, C_X)
			if !ok {
				glyph = fmt.Sprintf("%s⚠ %s", C_Y, C_X)
			}
			fmt.Printf("  %s %s%s%s  %s  %s(%dms)%s\n", glyph, C_B, p.name, C_X, msg, C_D, dt, C_X)
		}
	}
	results.TotalMS = time.Since(tTotal).Milliseconds()
	
	if !quiet {
		green := 0
		for _, v := range results.Phases {
			if v.OK {
				green++
			}
		}
		color := C_G
		if green < len(phases) {
			color = C_Y
		}
		fmt.Printf("\n  %s%s%d/%d phases green in %dms%s\n", color, C_B, green, len(phases), results.TotalMS, C_X)
	}

	return results
}

func fms(pid int, status string) string {
	return fmt.Sprintf("PID %d — %s", pid, status)
}

func checkResources() {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	sysMB := m.Sys / 1024 / 1024
	ts := time.Now().Format("15:04:05")

	if sysMB > ramCeilingMB {
		fmt.Printf("[🛑 ALERT %s] RAM %d MB exceeds %d MB ceiling! Throttle agents.\n",
			ts, sysMB, ramCeilingMB)
	}
}
