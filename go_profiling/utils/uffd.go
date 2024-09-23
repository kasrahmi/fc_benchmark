package utils

import (
	"fmt"
	"os/exec"
	"strconv"
	"strings"
)

type Uffd struct{}

func (u *Uffd) GetUffdPages() (int, error) {
	cmd := exec.Command("tmux", "capture-pane", "-t", "uffd_handler", "-p")
	output, err := cmd.Output()
	if err != nil {
		return -1, err
	}
	lines := strings.Split(strings.TrimSpace(string(output)), "\n")
	if len(lines) > 0 {
		lastLine := lines[len(lines)-1]
		pageCount, err := strconv.Atoi(strings.Fields(lastLine)[len(strings.Fields(lastLine))-1])
		if err != nil {
			return -1, err
		}
		return pageCount, nil
	}
	return -1, fmt.Errorf("no output captured")
}
