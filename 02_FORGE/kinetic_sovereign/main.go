// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
// //SOVEREIGN — Unified Go Interface (Anya + Pocket Squire)
package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// ── Styles ──────────────────────────────────────────────────────────

var (
	purple = lipgloss.Color("#7D52FF")
	green  = lipgloss.Color("#04B575")
	gray   = lipgloss.Color("#6272A4")

	docStyle = lipgloss.NewStyle().Margin(1, 2)

	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(purple).
			Padding(0, 1).
			BorderStyle(lipgloss.RoundedBorder()).
			BorderForeground(purple)

	tabStyle = lipgloss.NewStyle().
			Border(lipgloss.NormalBorder(), false, false, true, false).
			BorderForeground(gray).
			Padding(0, 2)

	activeTabStyle = tabStyle.Copy().
			BorderForeground(purple).
			Foreground(purple).
			Bold(true)

	statusStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(green)

	metricStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#8BE9FD"))

	footerStyle = lipgloss.NewStyle().
			Foreground(gray)
            
	anyStyle = lipgloss.NewStyle().
			Foreground(purple).
			Italic(true)
            
	purpleStyle = lipgloss.NewStyle().Foreground(purple)
	greenStyle  = lipgloss.NewStyle().Foreground(green)
	grayStyle   = lipgloss.NewStyle().Foreground(gray)
)

// ── Types ──────────────────────────────────────────────────────────

type tabId int

const (
	tabAnya tabId = iota
	tabSquire
	tabRemote
	tabVault
)

type model struct {
	activeTab tabId
	status    string
	cpuUsage  string
	recent    []string
	voice     voiceState
	remote    remoteState
	width     int
	height    int
}

type voiceState struct {
	Active   bool
	Waveform string
}

type remoteState struct {
	Connected bool
	Target    string
}

// ── Initial Model ──────────────────────────────────────────────────

func initialModel() model {
	return model{
		activeTab: tabAnya,
		status:    "RADIANT",
		cpuUsage:  "12.4%",
		recent:    []string{"[A2A] Sir Oracle synced with Modal Cloud.", "[A2A] Lady Apis foraging via Lightpanda."},
		voice: voiceState{
			Active:  false,
		},
		remote: remoteState{
			Connected: false,
			Target:    "100.118.224.52 (cybertronia)",
		},
	}
}

// ── Update ──────────────────────────────────────────────────────────

func (m model) Init() tea.Cmd {
	return tick()
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			return m, tea.Quit
		case "1":
			m.activeTab = tabAnya
		case "2":
			m.activeTab = tabSquire
		case "3":
			m.activeTab = tabRemote
		case "4":
			m.activeTab = tabVault
		case "v":
			m.voice.Active = !m.voice.Active
		case "c":
			if m.activeTab == tabRemote {
				go exec.Command("rustdesk.exe", "--connect", "100.118.224.52").Run()
				m.remote.Connected = true
			}
		}

	case tea.WindowSizeMsg:
		m.width, m.height = msg.Width, msg.Height

	case tickMsg:
		if m.voice.Active {
			m.voice.Waveform = generateWaveform()
		}
		return m, tick()
	}

	return m, nil
}

// ── View ────────────────────────────────────────────────────────────

func (m model) View() string {
	var s strings.Builder

	// Header
	header := titleStyle.Render("⚔️  KINETIC SOVEREIGN // OMNI-MODAL")
	s.WriteString(header + "\n\n")

	// Tabs
	tabs := []string{"[1] Anya (Live)", "[2] Pulse", "[3] Remote", "[4] Vault"}
	var renderedTabs []string
	for i, t := range tabs {
		if tabId(i) == m.activeTab {
			renderedTabs = append(renderedTabs, activeTabStyle.Render(t))
		} else {
			renderedTabs = append(renderedTabs, tabStyle.Render(t))
		}
	}
	s.WriteString(lipgloss.JoinHorizontal(lipgloss.Top, renderedTabs...) + "\n\n")

	// Content
	switch m.activeTab {
	case tabAnya:
		s.WriteString(m.renderAnya())
	case tabSquire:
		s.WriteString(m.renderSquire())
	case tabRemote:
		s.WriteString(m.renderRemote())
	case tabVault:
		s.WriteString("Secure Vault: AP2 Cryptographic Keys & Tokens\n")
		s.WriteString(grayStyle.Render("Identity: ak-5ccPxmJXw1BwPD2Hp8Yzye (ACTIVE)"))
	}

	// Footer
	footerText := fmt.Sprintf("W:%d H:%d | q: quit | [v] toggle voice", m.width, m.height)
	s.WriteString("\n\n" + footerStyle.Render(footerText))

	return docStyle.Render(s.String())
}

func (m model) renderAnya() string {
	var sb strings.Builder
	
	if m.voice.Active {
		sb.WriteString(anyStyle.Render("Anya is listening..."))
		sb.WriteString("\n\n")
		sb.WriteString(purpleStyle.Render(m.voice.Waveform))
		sb.WriteString("\n\n")
		sb.WriteString(grayStyle.Render("Connected to camelot-nexus (LiveKit)"))
	} else {
		sb.WriteString("Anya is on standby.\n\n")
		sb.WriteString(grayStyle.Render("Press [v] to ignite live voice interaction (Gemini-style)."))
	}
	
	return sb.String()
}

func (m model) renderSquire() string {
	status := statusStyle.Render(m.status)
	cpu := metricStyle.Render(m.cpuUsage)

	var sb strings.Builder
	sb.WriteString(fmt.Sprintf("System Pulse: %s\n", status))
	sb.WriteString(fmt.Sprintf("Load Index:   %s\n\n", cpu))
	sb.WriteString("A2A Stream:\n")
	for _, log := range m.recent {
		sb.WriteString("  " + log + "\n")
	}
	return sb.String()
}

func (m model) renderRemote() string {
	var sb strings.Builder
	sb.WriteString("Bifrost Bridge: Seamless Remote Desktop\n")
	sb.WriteString(fmt.Sprintf("Target: %s\n\n", m.remote.Target))
	
	if m.remote.Connected {
		sb.WriteString(greenStyle.Render("● BIFROST TUNNEL ACTIVE (RustDesk over Tailscale)"))
	} else {
		sb.WriteString(grayStyle.Render("Press [c] to initiate encrypted P2P session."))
	}
	return sb.String()
}

// ── Helpers ─────────────────────────────────────────────────────────

func generateWaveform() string {
	chars := []string{" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"}
	var w strings.Builder
	for i := 0; i < 30; i++ {
		w.WriteString(chars[time.Now().UnixNano()%int64(len(chars))])
	}
	return w.String()
}

type tickMsg time.Time

func tick() tea.Cmd {
	return tea.Every(100*time.Millisecond, func(t time.Time) tea.Msg {
		return tickMsg(t)
	})
}

// ── Main ────────────────────────────────────────────────────────────

func main() {
	p := tea.NewProgram(initialModel(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Sovereign failure: %v", err)
		os.Exit(1)
	}
}
