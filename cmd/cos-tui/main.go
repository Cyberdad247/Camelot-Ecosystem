package main

import (
	"fmt"
	"net"
	"os"
	"os/exec"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// Styling tokens (Obsidian and Luxora Gold)
var (
	obsidianColor = lipgloss.Color("#000000")
	goldColor     = lipgloss.Color("#D4AF37")
	greyColor     = lipgloss.Color("#7F8C8D")
	activeColor   = lipgloss.Color("#2ECC71")
	errorColor    = lipgloss.Color("#E74C3C")

	borderStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(goldColor).
			Background(obsidianColor).
			Padding(0, 1)

	headerStyle = lipgloss.NewStyle().
			Foreground(goldColor).
			Bold(true).
			Background(obsidianColor)

	descStyle = lipgloss.NewStyle().
			Foreground(greyColor)

	goldStyle = lipgloss.NewStyle().
			Foreground(goldColor)

	activeStatusStyle = lipgloss.NewStyle().
				Foreground(activeColor).
				Bold(true)

	offlineStatusStyle = lipgloss.NewStyle().
				Foreground(errorColor).
				Bold(true)
)

type RunicCommand struct {
	Name        string
	Description string
	Rune        string
	NeedsArg    bool
}

type statusMsg string
type outMsg string
type doneMsg struct {
	err error
}

type model struct {
	commands    []RunicCommand
	cursor      int
	gatewayStat string
	outputLog   []string
	typing      bool
	textInput   textinput.Model
	runningCmd  bool
}

func initialModel() model {
	ti := textinput.New()
	ti.Placeholder = "Enter target task / argument..."
	ti.Focus()
	ti.CharLimit = 156
	ti.Width = 50

	cmds := []RunicCommand{
		{Name: "//BOOT", Description: "Rehydrate session and UKG memory", Rune: "//BOOT", NeedsArg: false},
		{Name: "//STATUS", Description: "Probe active services and check port status", Rune: "//STATUS", NeedsArg: false},
		{Name: "//HEAL", Description: "Execute test repair loops on last error", Rune: "//HEAL", NeedsArg: false},
		{Name: "//SWARM", Description: "Launch parallel swarm tasks", Rune: "//SWARM", NeedsArg: true},
		{Name: "//NANO_SWARM", Description: "Expand and promote swarm components", Rune: "//NANO_SWARM_EXPAND", NeedsArg: true},
		{Name: "//EVOLVE_AND_FORGE", Description: "Run shadow forge self-mutation", Rune: "//EVOLVE_AND_FORGE", NeedsArg: true},
		{Name: "//CYBERTRON_ASCENSION", Description: "Initiate v1000 think tank audit", Rune: "//CYBERTRON_ASCENSION_THINK_TANK", NeedsArg: false},
	}

	return model{
		commands:    cmds,
		gatewayStat: "PROBING",
		textInput:   ti,
		outputLog:   []string{"[System Status]: TUI Initialized. Ready for runic dispatches."},
	}
}

func (m model) Init() tea.Cmd {
	return tea.Batch(
		textinput.Blink,
		m.checkGateway,
	)
}

func (m model) checkGateway() tea.Msg {
	conn, err := net.DialTimeout("tcp", "127.0.0.1:8001", 100*time.Millisecond)
	if err != nil {
		return statusMsg("OFFLINE")
	}
	conn.Close()
	return statusMsg("ACTIVE")
}

func (m model) runCommand(runicCmd RunicCommand, arg string) tea.Cmd {
	return func() tea.Msg {
		// Prepare target execution arguments
		execArgs := []string{"-m", "control_plane.runic_router", "--rune", runicCmd.Rune}
		if arg != "" {
			execArgs = append(execArgs, "--task", arg)
		} else {
			execArgs = append(execArgs, "--task", "status")
		}

		// Point to CAMELOT_OS directory specifically
		cwd, _ := os.Getwd()
		if !strings.HasSuffix(cwd, "CAMELOT_OS") {
			cwd = cwd + "\\CAMELOT_OS"
		}

		cmd := exec.Command("python", execArgs...)
		cmd.Dir = cwd

		out, err := cmd.CombinedOutput()
		if err != nil {
			return doneMsg{err: fmt.Errorf("%v: %s", err, string(out))}
		}
		return outMsg(string(out))
	}
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case tea.KeyMsg:
		if m.runningCmd {
			return m, nil
		}
		// Standard navigation
		if !m.typing {
			switch msg.String() {
			case "ctrl+c", "q":
				return m, tea.Quit

			case "up", "k":
				if m.cursor > 0 {
					m.cursor--
				}

			case "down", "j":
				if m.cursor < len(m.commands)-1 {
					m.cursor++
				}

			case "r":
				m.gatewayStat = "PROBING"
				return m, m.checkGateway

			case "enter":
				selected := m.commands[m.cursor]
				if selected.NeedsArg {
					m.typing = true
					m.textInput.Focus()
					return m, nil
				} else {
					m.runningCmd = true
					m.outputLog = []string{fmt.Sprintf("[Executing]: Spawning %s...", selected.Name)}
					return m, m.runCommand(selected, "")
				}
			}
		} else {
			// Argument input typing state
			switch msg.String() {
			case "enter":
				val := m.textInput.Value()
				m.typing = false
				m.runningCmd = true
				selected := m.commands[m.cursor]
				m.outputLog = []string{fmt.Sprintf("[Executing]: Spawning %s with task: '%s'...", selected.Name, val)}
				m.textInput.Reset()
				return m, m.runCommand(selected, val)

			case "esc":
				m.typing = false
				m.textInput.Reset()
				return m, nil
			}

			m.textInput, cmd = m.textInput.Update(msg)
			return m, cmd
		}

	case statusMsg:
		m.gatewayStat = string(msg)
		return m, nil

	case outMsg:
		lines := strings.Split(string(msg), "\n")
		m.outputLog = []string{}
		for _, line := range lines {
			trimmed := strings.TrimSpace(line)
			if trimmed != "" {
				m.outputLog = append(m.outputLog, trimmed)
			}
		}
		if len(m.outputLog) > 15 {
			m.outputLog = m.outputLog[len(m.outputLog)-15:]
		}
		return m, nil

	case doneMsg:
		m.runningCmd = false
		if msg.err != nil {
			m.outputLog = append(m.outputLog, fmt.Sprintf("[ERROR]: Process exited with error: %v", msg.err))
		} else {
			m.outputLog = append(m.outputLog, "[SUCCESS]: Execution completed successfully.")
		}
		return m, m.checkGateway
	}

	return m, nil
}

func (m model) View() string {
	var s strings.Builder

	// Header Panel
	gatewayLabel := activeStatusStyle.Render("Active")
	if m.gatewayStat == "OFFLINE" {
		gatewayLabel = offlineStatusStyle.Render("Offline")
	} else if m.gatewayStat == "PROBING" {
		gatewayLabel = headerStyle.Render("Probing...")
	}

	s.WriteString(headerStyle.Render(fmt.Sprintf(" [⚡] CAMELOT-OS APEX LAUNCHER          [Gateway: %s]\n", gatewayLabel)))
	s.WriteString(goldStyle.Render(" ─────────────────────────────────────────────────────────────\n"))

	// List Runic Commands
	s.WriteString(" Select a Runic Command to Execute:\n\n")
	for i, cmd := range m.commands {
		cursor := " "
		name := cmd.Name
		if m.cursor == i {
			cursor = goldStyle.Render(">")
			name = goldStyle.Render(cmd.Name)
		}
		s.WriteString(fmt.Sprintf("  %s [%s] %-22s %s\n", cursor, cursor, name, descStyle.Render(cmd.Description)))
	}

	s.WriteString("\n")

	// Prompt input panel
	if m.typing {
		s.WriteString(goldStyle.Render(" Argument Input (Press Esc to cancel):\n"))
		s.WriteString(fmt.Sprintf("  %s\n\n", m.textInput.View()))
	}

	// Output console panel
	s.WriteString(goldStyle.Render(" System Logs & Output:\n"))
	s.WriteString(goldStyle.Render(" ┌────────────────────────────────────────────────────────────┐\n"))
	for _, logLine := range m.outputLog {
		// Clean lines for box bounds
		truncated := logLine
		if len(truncated) > 58 {
			truncated = truncated[:55] + "..."
		}
		s.WriteString(fmt.Sprintf(" │ %-58s │\n", truncated))
	}
	// Pad empty space to maintain stable panel height
	for i := len(m.outputLog); i < 6; i++ {
		s.WriteString(" │                                                            │\n")
	}
	s.WriteString(goldStyle.Render(" └────────────────────────────────────────────────────────────┘\n"))

	// Hotkeys line
	s.WriteString(" [Enter] Select  |  [r] Refresh Gateway  |  [q] Quit  |  [Esc] Cancel")

	return borderStyle.Render(s.String())
}

func main() {
	p := tea.NewProgram(initialModel())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Alas, TUI encountered an error: %v", err)
		os.Exit(1)
	}
}
