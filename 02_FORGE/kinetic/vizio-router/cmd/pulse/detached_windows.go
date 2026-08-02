//go:build windows
package main

import (
	"os/exec"
	"syscall"
)

func setupDetached(cmd *exec.Cmd) {
	cmd.SysProcAttr = &syscall.SysProcAttr{
		CreationFlags: 0x00000010, // CREATE_NEW_CONSOLE
	}
}
