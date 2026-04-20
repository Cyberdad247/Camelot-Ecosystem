// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
// //FLEET — Aether Swarm Dashboard v2.0
// Reflects actual roster.yaml + Knights README (52 agents)
package main

import (
	"fmt"
	"math/rand"
	"os"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// ── Styles ──────────────────────────────────────────────────────────

var (
	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#7D52FF")).
			Padding(1, 2).
			BorderStyle(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("#7D52FF"))

	sectionStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#FFD700")).
			PaddingTop(1)

	knightStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#04B575")).
			Bold(true).
			Width(20)

	roleStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#8BE9FD")).
			Width(22)

	statusActive = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#50FA7B")).
			Bold(true)

	statusIdle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#6272A4"))

	statusOffline = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#FF5555"))

	barFull = lipgloss.NewStyle().
		Foreground(lipgloss.Color("#50FA7B"))

	barEmpty = lipgloss.NewStyle().
		Foreground(lipgloss.Color("#44475A"))

	footerStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#6272A4")).
			PaddingTop(1)

	tabActive = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#FFD700")).
			Background(lipgloss.Color("#44475A")).
			Padding(0, 2)

	tabInactive = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#6272A4")).
			Padding(0, 2)
)

// ── Data ────────────────────────────────────────────────────────────

type Knight struct {
	Name   string
	Role   string
	Layer  string
	Engine string // Foundry council only
	Weight string // Foundry council only
	Status string
	Load   int
}

type Section struct {
	Title   string
	Knights []Knight
}

type model struct {
	sections []Section
	tab      int // 0=Roster, 1=Foundry, 2=Squires
	ticks    int
}

func roster() []Section {
	return []Section{
		{
			Title: "I. SOVEREIGN TRIUMVIRATE",
			Knights: []Knight{
				{Name: "MERLIN_\u03A9", Role: "Archwizard", Layer: "L3", Status: "ACTIVE", Load: 72},
				{Name: "ANYA_\u03A9", Role: "Compiler", Layer: "L7", Status: "ACTIVE", Load: 65},
				{Name: "LUKAS_\u03A9", Role: "Kinetic Hand", Layer: "L2", Status: "IDLE", Load: 10},
				{Name: "MORGANA_\u03A9", Role: "Substrate Swarm", Layer: "L1", Status: "IDLE", Load: 5},
			},
		},
		{
			Title: "II. ORDER I — ARCHITECTS",
			Knights: []Knight{
				{Name: "SIR_SYSTEMA", Role: "Grand Architect", Layer: "L3", Status: "IDLE", Load: 0},
				{Name: "SIR_SYNTHESIS", Role: "Neurosym Architect", Layer: "L3", Status: "IDLE", Load: 0},
				{Name: "SIR_LANCELOT", Role: "Master Builder", Layer: "L3", Status: "IDLE", Load: 0},
			},
		},
		{
			Title: "III. ORDER II — STRATEGISTS",
			Knights: []Knight{
				{Name: "GEN_STRATEGOS", Role: "Strategic Architect", Layer: "L5", Status: "IDLE", Load: 0},
				{Name: "SIR_ORACLE", Role: "Seeker/Planner", Layer: "L5", Status: "IDLE", Load: 0},
				{Name: "ANYA_PLANNER", Role: "Tactical Exec", Layer: "L5", Status: "IDLE", Load: 0},
			},
		},
		{
			Title: "IV. ORDER III — TRUTH SEEKERS",
			Knights: []Knight{
				{Name: "LADY_VERITAS", Role: "Truth Sentinel", Layer: "L6", Status: "IDLE", Load: 0},
				{Name: "SIR_OCTAVIAN", Role: "High Warden", Layer: "L6", Status: "SCANNING", Load: 20},
				{Name: "SIR_ZENITH", Role: "Sentinel", Layer: "L6", Status: "IDLE", Load: 0},
				{Name: "SIR_AURELIUS", Role: "Alchemist (Fin)", Layer: "L6", Status: "IDLE", Load: 0},
				{Name: "ELDER_KAELEN", Role: "Context Sentinel", Layer: "L6", Status: "IDLE", Load: 0},
			},
		},
		{
			Title: "V. ORDER IV — BUILDERS",
			Knights: []Knight{
				{Name: "SIR_SYNTAX", Role: "Code Architect", Layer: "L2", Status: "IDLE", Load: 0},
				{Name: "SIR_FORGEMASTER", Role: "Agentic Smith", Layer: "L2", Status: "IDLE", Load: 0},
				{Name: "SIR_STITCH", Role: "Interface Architect", Layer: "L2", Status: "IDLE", Load: 0},
				{Name: "SIR_ALCHEMIST", Role: "Optimization Smith", Layer: "L2", Status: "IDLE", Load: 0},
				{Name: "BARON_VAELEN", Role: "Iron Industrialist", Layer: "L2", Status: "IDLE", Load: 0},
			},
		},
		{
			Title: "VI. ORDER V — CREATIVES",
			Knights: []Knight{
				{Name: "SIR_VISAGE", Role: "The Auteur", Layer: "L4", Status: "IDLE", Load: 0},
				{Name: "SIR_SONUS", Role: "Lyrical Engine", Layer: "L4", Status: "IDLE", Load: 0},
				{Name: "SIR_BARD", Role: "Storyteller", Layer: "L4", Status: "IDLE", Load: 0},
				{Name: "LADY_AURA", Role: "Brand Voice", Layer: "L4", Status: "IDLE", Load: 0},
				{Name: "DAME_SPARKLE", Role: "The Voice", Layer: "L4", Status: "IDLE", Load: 0},
			},
		},
		{
			Title: "VII. ORDER VI — SCOUTS",
			Knights: []Knight{
				{Name: "LADY_APIS", Role: "Swarm Mother", Layer: "L4", Status: "FORAGING", Load: 88},
				{Name: "DR_SYNTHETICA", Role: "Data Analytics", Layer: "L4", Status: "IDLE", Load: 0},
				{Name: "ROOT_STERLING", Role: "SEO & Growth", Layer: "L4", Status: "IDLE", Load: 0},
				{Name: "SIR_PERCIVAL", Role: "High Scout", Layer: "L4", Status: "IDLE", Load: 0},
				{Name: "SIR_HERMES", Role: "Courier", Layer: "L4", Status: "IDLE", Load: 0},
			},
		},
		{
			Title: "VIII. ORDER VII — OPERATORS",
			Knights: []Knight{
				{Name: "SIR_STERLING", Role: "Rainmaker", Layer: "L5", Status: "IDLE", Load: 0},
				{Name: "GRACE_HARMONIA", Role: "Diplomat", Layer: "L5", Status: "IDLE", Load: 0},
				{Name: "WILLOW_FLUX", Role: "Digital Experience", Layer: "L5", Status: "IDLE", Load: 0},
			},
		},
		{
			Title: "IX. PALADIN SWARM (NDR+S)",
			Knights: []Knight{
				{Name: "ADEPT_ARIS", Role: "Logician", Layer: "L3", Status: "IDLE", Load: 0},
				{Name: "ADEPT_MAYA", Role: "Vibe Architect", Layer: "L4", Status: "IDLE", Load: 0},
				{Name: "ADEPT_VEGA", Role: "Strategist", Layer: "L5", Status: "IDLE", Load: 0},
				{Name: "ADEPT_KAELEN", Role: "Scribe", Layer: "L6", Status: "IDLE", Load: 0},
			},
		},
	}
}

func foundry() []Section {
	return []Section{
		{
			Title: "FOUNDRY COUNCIL (Multi-Engine Matrix)",
			Knights: []Knight{
				{Name: "SIR_BORIS", Role: "The Anvil", Layer: "L5", Engine: "Claude Code", Weight: "0.85/W_orch", Status: "ACTIVE", Load: 85},
				{Name: "SIR_HELIO", Role: "Context Lord", Layer: "L5", Engine: "Gemini CLI", Weight: "0.90/W_ctx", Status: "STANDBY", Load: 30},
				{Name: "SIR_CODEX", Role: "Velocity", Layer: "L5", Engine: "OpenAI Codex", Weight: "0.75/W_vel", Status: "STANDBY", Load: 15},
				{Name: "SIR_GHOST", Role: "Zero-Trust", Layer: "L5", Engine: "Local Qwen", Weight: "1.00/W_priv", Status: "OFFLINE", Load: 0},
				{Name: "SIR_LIBERTE", Role: "Sovereignty", Layer: "L5", Engine: "Open Source", Weight: "0.80/W_sov", Status: "OFFLINE", Load: 0},
			},
		},
		{
			Title: "EXCALIBUR ROSTER AGENTS",
			Knights: []Knight{
				{Name: "SIR_FORGE", Role: "Builder", Layer: "L2", Engine: "Gemini Flash", Weight: "-", Status: "IDLE", Load: 0},
				{Name: "SIR_SENTINEL", Role: "Warden", Layer: "L6", Engine: "Gemini Flash", Weight: "-", Status: "IDLE", Load: 0},
				{Name: "SIR_VALERIAN", Role: "Finance", Layer: "L5", Engine: "Gemini Flash", Weight: "-", Status: "IDLE", Load: 0},
			},
		},
	}
}

func squires() []Section {
	return []Section{
		{
			Title: "SQUIRE COLONY — CLARITY_CORE v1.0.0",
			Knights: []Knight{
				{Name: "SQ_INDEX", Role: "The Scout", Layer: "L2", Engine: "Python BTree", Status: "IDLE", Load: 0},
				{Name: "SQ_GHOST", Role: "The Exorcist", Layer: "L2", Engine: "psutil PID", Status: "IDLE", Load: 0},
				{Name: "SQ_VECTOR", Role: "The Librarian", Layer: "L4", Engine: "Embeddings", Status: "IDLE", Load: 0},
				{Name: "SQ_SWEEP", Role: "The Janitor", Layer: "L2", Engine: "Vault HITL", Status: "IDLE", Load: 0},
				{Name: "SQ_SCAN", Role: "The Forager", Layer: "L4", Engine: "Import Graph", Status: "IDLE", Load: 0},
				{Name: "SQ_JUDGE", Role: "Discriminator", Layer: "L4", Engine: "Rules Engine", Status: "IDLE", Load: 0},
				{Name: "SQ_SENTINEL", Role: "The Safety", Layer: "L6", Engine: "Antigravity", Status: "IDLE", Load: 0},
				{Name: "SQ_MASON", Role: "The Optimizer", Layer: "L4", Engine: "Symbolect UKG", Status: "IDLE", Load: 0},
			},
		},
	}
}

// ── Model ───────────────────────────────────────────────────────────

func initialModel() model {
	return model{
		sections: roster(),
		tab:      0,
		ticks:    0,
	}
}

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
			m.tab = 0
			m.sections = roster()
		case "2":
			m.tab = 1
			m.sections = foundry()
		case "3":
			m.tab = 2
			m.sections = squires()
		}
	case tickMsg:
		m.ticks++
		for si := range m.sections {
			for ki := range m.sections[si].Knights {
				k := &m.sections[si].Knights[ki]
				if k.Status == "ACTIVE" || k.Status == "SCANNING" || k.Status == "FORAGING" || k.Status == "BUILDING" {
					delta := rand.Intn(11) - 3 // -3 to +7
					k.Load += delta
					if k.Load > 100 {
						k.Load = 100
					}
					if k.Load < 5 {
						k.Load = 5
					}
				}
			}
		}
		return m, tick()
	}
	return m, nil
}

func (m model) View() string {
	s := titleStyle.Render("⚔️  CAMELOT_OS // AETHER SWARM (FLEET) v2.0") + "\n"

	// Tab bar
	tabs := []string{"[1] Roster", "[2] Foundry", "[3] Squires"}
	var tabLine string
	for i, t := range tabs {
		if i == m.tab {
			tabLine += tabActive.Render(t) + " "
		} else {
			tabLine += tabInactive.Render(t) + " "
		}
	}
	s += tabLine + "\n"

	// Sections
	for _, sec := range m.sections {
		s += sectionStyle.Render("── "+sec.Title) + "\n"
		for _, k := range sec.Knights {
			name := knightStyle.Render(k.Name)
			role := roleStyle.Render(k.Role)

			// Status styling
			var st string
			switch k.Status {
			case "ACTIVE", "BUILDING", "FORAGING", "SCANNING":
				st = statusActive.Render(k.Status)
			case "STANDBY", "IDLE":
				st = statusIdle.Render(k.Status)
			default:
				st = statusOffline.Render(k.Status)
			}

			// Load bar
			filled := k.Load / 10
			empty := 10 - filled
			bar := barFull.Render(strings.Repeat("█", filled)) + barEmpty.Render(strings.Repeat("░", empty))

			line := fmt.Sprintf("%s %s %-10s %s %3d%%", name, role, st, bar, k.Load)
			if k.Engine != "" {
				line += fmt.Sprintf("  [%s]", k.Engine)
			}
			s += line + "\n"
		}
	}

	// Footer
	total := 0
	active := 0
	for _, sec := range m.sections {
		for _, k := range sec.Knights {
			total++
			if k.Status == "ACTIVE" || k.Status == "SCANNING" || k.Status == "FORAGING" || k.Status == "BUILDING" {
				active++
			}
		}
	}
	s += footerStyle.Render(fmt.Sprintf("TICK: %d | AGENTS: %d/%d active | RAM ceiling: 8GB", m.ticks, active, total))
	s += "\n" + footerStyle.Render("Press 1/2/3 to switch tabs | q to quit")

	return s
}

// ── Tick ─────────────────────────────────────────────────────────────

type tickMsg time.Time

func tick() tea.Cmd {
	return tea.Every(time.Second, func(t time.Time) tea.Msg {
		return tickMsg(t)
	})
}

// ── Main ────────────────────────────────────────────────────────────

func main() {
	p := tea.NewProgram(initialModel(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Alas, the fleet has crashed: %v", err)
		os.Exit(1)
	}
}
