// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — VIZION TELEMETRY v1.0
// Kinetic Layer monitor for Saltare Gateway + Loom services.
// Build: go build -ldflags="-s -w" -o vizion-telemetry.exe .
package main

import (
	"fmt"
	"net"
	"os"
	"os/exec"
	"runtime"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/shirou/gopsutil/v3/cpu"
	"github.com/shirou/gopsutil/v3/mem"
	"github.com/shirou/gopsutil/v3/process"
)

// ── Styles ────────────────────────────────────────────────────────────────────

var (
	cyan    = lipgloss.Color("#00d4ff")
	orange  = lipgloss.Color("#ff6a00")
	green   = lipgloss.Color("#2ecc71")
	red     = lipgloss.Color("#e74c3c")
	yellow  = lipgloss.Color("#ffcc00")
	dim     = lipgloss.Color("#3a4a5a")
	white   = lipgloss.Color("#c8d8e8")
	bg      = lipgloss.Color("#03080f")
	bgPanel = lipgloss.Color("#0a1628")

	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(cyan).
			Background(bg).
			Padding(0, 2).
			BorderForeground(cyan).
			Border(lipgloss.DoubleBorder(), false, false, true, false)

	panelStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(cyan).
			Background(bgPanel).
			Padding(0, 1)

	panelTitleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(yellow).
			Background(bgPanel)

	onlineStyle  = lipgloss.NewStyle().Foreground(green).Bold(true)
	offlineStyle = lipgloss.NewStyle().Foreground(red).Bold(true)
	dimStyle     = lipgloss.NewStyle().Foreground(dim)
	labelStyle   = lipgloss.NewStyle().Foreground(cyan)
	valueStyle   = lipgloss.NewStyle().Foreground(white)
	warnStyle    = lipgloss.NewStyle().Foreground(orange).Bold(true)

	footerStyle = lipgloss.NewStyle().
			Foreground(dim).
			BorderForeground(dim).
			Border(lipgloss.NormalBorder(), true, false, false, false).
			Padding(0, 1)
)

// ── Service definitions ───────────────────────────────────────────────────────

type Service struct {
	Name   string
	Port   int
	Status bool
	Ping   time.Duration
}

var services = []Service{
	{Name: "Saltare Gateway", Port: 8085},
	{Name: "Control Plane", Port: 8080},
	{Name: "Excalibur API", Port: 8000},
	{Name: "MCP Edge", Port: 3001},
	{Name: "Qdrant Vector DB", Port: 6333},
	{Name: "Rotel OTEL", Port: 4317},
	{Name: "Holotable UI", Port: 3000},
	{Name: "Gradio Sandbox", Port: 7860},
}

type Loom struct {
	ID      string
	Name    string
	Port    int
	Status  bool
	Latency time.Duration
	Mode    string
}

var looms = []Loom{
	{ID: "#101", Name: "AI Receptionist", Port: 8101, Mode: "voice/chat"},
	{ID: "#209", Name: "AI Story Studio", Port: 8209, Mode: "generative"},
}

// ── Model ─────────────────────────────────────────────────────────────────────

type tickMsg time.Time
type metricsMsg struct {
	cpuPct float64
	ramPct float64
	ramGB  float64
	ramMax float64
	procs  int
}
type serviceMsg []Service
type loomMsg []Loom
type gpuMsg struct {
	name    string
	utilPct float64
	vramGB  float64
	vramMax float64
	ok      bool
}

type model struct {
	spinner  spinner.Model
	tick     int
	width    int
	height   int
	cpu      float64
	ram      float64
	ramGB    float64
	ramMax   float64
	procs    int
	gpuName  string
	gpuUtil  float64
	vramGB   float64
	vramMax  float64
	gpuOk    bool
	services []Service
	looms    []Loom
	log      []string
	uptime   time.Time
}

func initialModel() model {
	s := spinner.New()
	s.Spinner = spinner.Dot
	s.Style = lipgloss.NewStyle().Foreground(cyan)
	return model{
		spinner:  s,
		services: services,
		looms:    looms,
		uptime:   time.Now(),
		log:      []string{"BOOT: VIZION TELEMETRY v1.0", "BOOT: Kinetic Layer Monitor active"},
	}
}

// ── Commands ──────────────────────────────────────────────────────────────────

func tick() tea.Cmd {
	return tea.Tick(2*time.Second, func(t time.Time) tea.Msg {
		return tickMsg(t)
	})
}

func gatherGPU() tea.Cmd {
	return func() tea.Msg {
		// Try nvidia-smi first (NVIDIA GPU)
		out, err := exec.Command("nvidia-smi",
			"--query-gpu=name,utilization.gpu,memory.used,memory.total",
			"--format=csv,noheader,nounits").Output()
		if err == nil {
			parts := strings.Split(strings.TrimSpace(string(out)), ",")
			if len(parts) >= 4 {
				name := strings.TrimSpace(parts[0])
				util := 0.0
				vused := 0.0
				vtotal := 0.0
				fmt.Sscanf(strings.TrimSpace(parts[1]), "%f", &util)
				fmt.Sscanf(strings.TrimSpace(parts[2]), "%f", &vused)
				fmt.Sscanf(strings.TrimSpace(parts[3]), "%f", &vtotal)
				return gpuMsg{name: name, utilPct: util,
					vramGB: vused / 1024.0, vramMax: vtotal / 1024.0, ok: true}
			}
		}
		// Fallback: WMIC (Windows — any GPU)
		out, err = exec.Command("wmic", "path", "win32_VideoController",
			"get", "Name,AdapterRAM", "/format:csv").Output()
		if err == nil {
			lines := strings.Split(string(out), "\n")
			for _, line := range lines {
				parts := strings.Split(strings.TrimSpace(line), ",")
				if len(parts) >= 3 && parts[2] != "" && parts[2] != "Name" {
					ramBytes := 0.0
					fmt.Sscanf(strings.TrimSpace(parts[1]), "%f", &ramBytes)
					return gpuMsg{
						name:    strings.TrimSpace(parts[2]),
						utilPct: -1, // WMIC can't report live util
						vramGB:  0,
						vramMax: ramBytes / 1e9,
						ok:      true,
					}
				}
			}
		}
		return gpuMsg{name: "No GPU detected", ok: false}
	}
}

func gatherMetrics() tea.Cmd {
	return func() tea.Msg {
		pcts, _ := cpu.Percent(200*time.Millisecond, false)
		cpuPct := 0.0
		if len(pcts) > 0 {
			cpuPct = pcts[0]
		}
		vmStat, _ := mem.VirtualMemory()
		procs, _ := process.Pids()
		return metricsMsg{
			cpuPct: cpuPct,
			ramPct: vmStat.UsedPercent,
			ramGB:  float64(vmStat.Used) / 1e9,
			ramMax: float64(vmStat.Total) / 1e9,
			procs:  len(procs),
		}
	}
}

func probeServices(svcs []Service, lms []Loom) tea.Cmd {
	return func() tea.Msg {
		updated := make([]Service, len(svcs))
		for i, s := range svcs {
			start := time.Now()
			conn, err := net.DialTimeout("tcp", fmt.Sprintf("127.0.0.1:%d", s.Port), 400*time.Millisecond)
			if err == nil {
				conn.Close()
				updated[i] = Service{Name: s.Name, Port: s.Port, Status: true, Ping: time.Since(start)}
			} else {
				updated[i] = Service{Name: s.Name, Port: s.Port, Status: false}
			}
		}
		updatedLooms := make([]Loom, len(lms))
		for i, l := range lms {
			start := time.Now()
			conn, err := net.DialTimeout("tcp", fmt.Sprintf("127.0.0.1:%d", l.Port), 400*time.Millisecond)
			if err == nil {
				conn.Close()
				updatedLooms[i] = Loom{ID: l.ID, Name: l.Name, Port: l.Port, Mode: l.Mode, Status: true, Latency: time.Since(start)}
			} else {
				updatedLooms[i] = Loom{ID: l.ID, Name: l.Name, Port: l.Port, Mode: l.Mode, Status: false}
			}
		}
		// svc msg sent first; looms piggyback in same batch via separate msg type
		_ = updatedLooms
		return serviceMsg(updated)
	}
}

// ── Update ────────────────────────────────────────────────────────────────────

func (m model) Init() tea.Cmd {
	return tea.Batch(tick(), gatherMetrics(), gatherGPU(), probeServices(m.services, m.looms), m.spinner.Tick)
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			return m, tea.Quit
		case "r":
			m.addLog("MANUAL REFRESH triggered")
			return m, tea.Batch(gatherMetrics(), probeServices(m.services, m.looms))
		}

	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height

	case gpuMsg:
		m.gpuName = msg.name
		m.gpuUtil = msg.utilPct
		m.vramGB = msg.vramGB
		m.vramMax = msg.vramMax
		m.gpuOk = msg.ok

	case tickMsg:
		m.tick++
		cmds := []tea.Cmd{tick(), gatherMetrics(), probeServices(m.services, m.looms)}
		if m.tick%5 == 0 { // probe GPU every 10s (every 5th 2s tick)
			cmds = append(cmds, gatherGPU())
		}
		return m, tea.Batch(cmds...)

	case spinner.TickMsg:
		var cmd tea.Cmd
		m.spinner, cmd = m.spinner.Update(msg)
		return m, cmd

	case metricsMsg:
		m.cpu = msg.cpuPct
		m.ram = msg.ramPct
		m.ramGB = msg.ramGB
		m.ramMax = msg.ramMax
		m.procs = msg.procs

	case serviceMsg:
		m.services = []Service(msg)
		online := 0
		for _, s := range m.services {
			if s.Status {
				online++
			}
		}
		m.addLog(fmt.Sprintf("PROBE: %d/%d services online", online, len(m.services)))
	}

	return m, nil
}

func (m *model) addLog(msg string) {
	ts := time.Now().Format("15:04:05")
	m.log = append(m.log, fmt.Sprintf("[%s] %s", ts, msg))
	if len(m.log) > 12 {
		m.log = m.log[len(m.log)-12:]
	}
}

// ── View ──────────────────────────────────────────────────────────────────────

func bar(pct float64, width int, fill lipgloss.Color) string {
	filled := int(pct / 100 * float64(width))
	if filled > width {
		filled = width
	}
	empty := width - filled
	b := lipgloss.NewStyle().Foreground(fill).Render(strings.Repeat("█", filled))
	b += dimStyle.Render(strings.Repeat("░", empty))
	return b
}

func statusDot(online bool) string {
	if online {
		return onlineStyle.Render("● ONLINE ")
	}
	return offlineStyle.Render("● OFFLINE")
}

func (m model) View() string {
	if m.width == 0 {
		return "Initializing VIZION TELEMETRY..."
	}

	upDuration := time.Since(m.uptime).Round(time.Second)
	os := runtime.GOOS + "/" + runtime.GOARCH

	// ── HEADER ──
	header := titleStyle.Width(m.width - 2).Render(
		fmt.Sprintf("⚔  VIZION TELEMETRY v1.0  |  Camelot Apex OS  |  Uptime: %s  |  OS: %s",
			upDuration, os),
	)

	halfW := (m.width - 4) / 2

	// ── METRICS PANEL ──
	cpuColor := green
	if m.cpu > 80 {
		cpuColor = red
	} else if m.cpu > 60 {
		cpuColor = orange
	}
	ramColor := green
	if m.ram > 80 {
		ramColor = red
	} else if m.ram > 60 {
		ramColor = orange
	}

	gpuColor := green
	if m.gpuUtil > 80 {
		gpuColor = red
	} else if m.gpuUtil > 60 {
		gpuColor = orange
	}
	gpuLine := ""
	if m.gpuOk && m.gpuUtil >= 0 {
		gpuLine = fmt.Sprintf("%s %s %s",
			labelStyle.Render("GPU  "),
			bar(m.gpuUtil, 20, gpuColor),
			valueStyle.Render(fmt.Sprintf(" %.0f%% VRAM %.1f/%.1fGB", m.gpuUtil, m.vramGB, m.vramMax)))
	} else if m.gpuOk {
		gpuLine = fmt.Sprintf("%s %s",
			labelStyle.Render("GPU  "),
			valueStyle.Render(fmt.Sprintf("%s  VRAM %.1fGB", m.gpuName, m.vramMax)))
	} else {
		gpuLine = fmt.Sprintf("%s %s", labelStyle.Render("GPU  "), dimStyle.Render("not detected"))
	}
	metricsLines := []string{
		panelTitleStyle.Render("SYSTEM METRICS"),
		"",
		fmt.Sprintf("%s %s %s",
			labelStyle.Render("CPU  "),
			bar(m.cpu, 20, cpuColor),
			valueStyle.Render(fmt.Sprintf(" %.1f%%", m.cpu))),
		fmt.Sprintf("%s %s %s",
			labelStyle.Render("RAM  "),
			bar(m.ram, 20, ramColor),
			valueStyle.Render(fmt.Sprintf(" %.1f%% (%.1f/%.1fGB)", m.ram, m.ramGB, m.ramMax))),
		gpuLine,
		"",
		fmt.Sprintf("%s %s", labelStyle.Render("PROCS "), valueStyle.Render(fmt.Sprintf("%d", m.procs))),
		fmt.Sprintf("%s %s", labelStyle.Render("TICK  "), valueStyle.Render(fmt.Sprintf("#%d", m.tick))),
		fmt.Sprintf("%s %s", labelStyle.Render("PROBE "), dimStyle.Render("every 2s")),
	}
	metricsPanel := panelStyle.Width(halfW).Render(strings.Join(metricsLines, "\n"))

	// ── LOOM PANEL ──
	loomLines := []string{panelTitleStyle.Render("LOOM STATUS"), ""}
	for _, l := range m.looms {
		ping := ""
		if l.Status {
			ping = dimStyle.Render(fmt.Sprintf(" %dms", l.Latency.Milliseconds()))
		}
		loomLines = append(loomLines,
			fmt.Sprintf("%s %s %s %s%s",
				labelStyle.Render(l.ID),
				valueStyle.Render(fmt.Sprintf("%-20s", l.Name)),
				statusDot(l.Status),
				dimStyle.Render(l.Mode),
				ping,
			),
		)
	}
	loomPanel := panelStyle.Width(halfW).Render(strings.Join(loomLines, "\n"))

	topRow := lipgloss.JoinHorizontal(lipgloss.Top, metricsPanel, "  ", loomPanel)

	// ── SERVICES PANEL ──
	colW := (m.width - 6) / 4
	svcLines := []string{panelTitleStyle.Render("SERVICE HEALTH — KINETIC LAYER"), ""}
	for _, s := range m.services {
		ping := ""
		if s.Status && s.Ping > 0 {
			ping = dimStyle.Render(fmt.Sprintf(" %dms", s.Ping.Milliseconds()))
		}
		row := fmt.Sprintf("%-*s  %s  :%d%s",
			colW, valueStyle.Render(s.Name),
			statusDot(s.Status),
			s.Port,
			ping,
		)
		svcLines = append(svcLines, row)
	}
	svcPanel := panelStyle.Width(m.width - 4).Render(strings.Join(svcLines, "\n"))

	// ── LOG PANEL ──
	logLines := []string{panelTitleStyle.Render("KINETIC LOG"), ""}
	for _, l := range m.log {
		logLines = append(logLines, dimStyle.Render(l))
	}
	logPanel := panelStyle.Width(m.width - 4).Render(strings.Join(logLines, "\n"))

	// ── FOOTER ──
	spinnerView := m.spinner.View()
	footer := footerStyle.Width(m.width - 2).Render(
		fmt.Sprintf("%s Probing...   [r] Refresh   [q] Quit   Saltare:8085  Telemetry:4317", spinnerView),
	)

	return lipgloss.JoinVertical(lipgloss.Left,
		header,
		"",
		topRow,
		"",
		svcPanel,
		"",
		logPanel,
		"",
		footer,
	)
}

// ── Entry point ───────────────────────────────────────────────────────────────

func main() {
	p := tea.NewProgram(
		initialModel(),
		tea.WithAltScreen(),
		tea.WithMouseCellMotion(),
	)
	if _, err := p.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "vizion-telemetry error: %v\n", err)
		os.Exit(1)
	}
}
