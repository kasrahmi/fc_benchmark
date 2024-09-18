package utils

import (
	"fmt"
    "os/exec"
	"strings"
)

type Tmux struct{}

func (t *Tmux) CreateSession(sessionName string) {
    exec.Command("tmux", "new-session", "-d", "-s", sessionName).Run()
}

func (t *Tmux) KillSession(sessionName string) {
    exec.Command("tmux", "kill-session", "-t", sessionName).Run()
}

func (t *Tmux) RunCommandInSession(sessionName, command string) {
    exec.Command("tmux", "send", "-t", sessionName, fmt.Sprintf(`"%s"`, command), "Enter").Run()
}

func (t *Tmux) CaptureLastStdoutLine(sessionName string) (string, error) {
    cmd := exec.Command("tmux", "capture-pane", "-t", sessionName, "-p")
    output, err := cmd.Output()
    if err != nil {
        return "", err
    }
    lines := strings.Split(strings.TrimSpace(string(output)), "\n")
    return lines[len(lines)-1], nil
}
