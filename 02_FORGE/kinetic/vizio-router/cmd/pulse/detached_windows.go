//go:build windows
package main

import (
	"os"
	"os/exec"
	"syscall"
)

func setupDetached(cmd *exec.Cmd) {
	flags := uint32(0x08000000) // CREATE_NO_WINDOW (Silent background daemon)
	if os.Getenv("CAMELOT_VISIBLE_CHILDREN") == "1" {
		flags = 0x00000010 // CREATE_NEW_CONSOLE (Visible debugging windows)
	}
	cmd.SysProcAttr = &syscall.SysProcAttr{
		CreationFlags: flags,
	}
}
