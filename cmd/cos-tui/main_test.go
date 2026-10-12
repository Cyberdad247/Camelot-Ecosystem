package main

import (
	"testing"
)

func TestModelInitialization(t *testing.T) {
	m := initialModel()

	if len(m.commands) == 0 {
		t.Error("Expected commands list to not be empty")
	}

	expectedFirstCmd := "//BOOT"
	if m.commands[0].Name != expectedFirstCmd {
		t.Errorf("Expected first command to be %s, got %s", expectedFirstCmd, m.commands[0].Name)
	}

	if m.gatewayStat != "PROBING" {
		t.Errorf("Expected initial gateway state to be PROBING, got %s", m.gatewayStat)
	}

	if m.typing {
		t.Error("Expected initial typing state to be false")
	}

	if m.runningCmd {
		t.Error("Expected initial runningCmd state to be false")
	}
}
