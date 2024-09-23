package utils

import (
	"fmt"
	"os/exec"
	"path/filepath"
	"time"

	log "github.com/sirupsen/logrus"
)

type MemoryProfiler struct {
	Language      string
	Experiment    string
	ServerCommand string
	ClientCommand string
	ServerPath    string
	ClientPath    string
	FCClient      FirecrackerVM
}

// NewMemoryProfiler initializes a MemoryProfiler based on language and experiment
func NewMemoryProfiler(language, experiment, serverCommand, clientCommand string) (*MemoryProfiler, error) {
	serverPath := filepath.Join("/root/workload", language, experiment)
	clientPath := filepath.Join(WorkloadPath, language, experiment)

	if serverCommand == "" && clientCommand == "" {
		switch language {
		case "python":
			serverCommand = fmt.Sprintf("python3 %s/server.py", serverPath)
			clientCommand = fmt.Sprintf("python3 %s/client.py", clientPath)
		case "cpp":
			serverCommand = fmt.Sprintf("%s/server", serverPath)
			clientCommand = fmt.Sprintf("%s/client", clientPath)
		case "node":
			serverCommand = fmt.Sprintf("node %s/server.js", serverPath)
			clientCommand = fmt.Sprintf("node %s/client.js", clientPath)
		default:
			return nil, fmt.Errorf("unsupported language")
		}
	} else if serverCommand == "" || clientCommand == "" {
		return nil, fmt.Errorf("both server and client command must be provided")
	}

	fcClient := FirecrackerVM{SessionName: fmt.Sprintf("%s_%s", language, experiment)}

	return &MemoryProfiler{
		Language:      language,
		Experiment:    experiment,
		ServerCommand: serverCommand,
		ClientCommand: clientCommand,
		ServerPath:    serverPath,
		ClientPath:    clientPath,
		FCClient:      fcClient,
	}, nil
}

func (m *MemoryProfiler) StartNewVM() {
	log.Info("Starting new VM")
	m.FCClient.StartFCVMM()
	time.Sleep(3 * time.Second)
	m.FCClient.CreateVM()
	time.Sleep(3 * time.Second)
}

func (m *MemoryProfiler) RunServer() {
	log.Infof("Running server: %s", m.ServerCommand)
	m.FCClient.RunCommandOnVMTmux(m.ServerCommand)
	time.Sleep(3 * time.Second)
}

func (m *MemoryProfiler) WarmupServer(loop int) {
	log.Infof("Warming up server")
	if loop == 0 {
		loop = 10
	}

	successCount := 0
	failCount := 0
	for successCount < loop && failCount < loop {
		log.Debugf("Warming up %d/%d", successCount, loop)
		output, err := m.InvokeServer()
		if err != nil {
			log.Warnf("Failed to invoke server: %v\n", err)
			failCount++
		} else {
			log.Debugf("Server response during warmup: %s\n", output)
			successCount++
		}
		time.Sleep(5 * time.Second)
	}
}

func (m *MemoryProfiler) InvokeServer() (string, error) {
	log.Debugf("Invoking server")

	// Create the command for client invocation
	cmd := exec.Command("bash", "-c", m.ClientCommand)

	// Capture the output of the command
	output, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("server invocation failed: %v", err)
	}

	// Convert the byte output to a string and return it
	return string(output), nil
}

func (m *MemoryProfiler) TakeSnapshot() {
	log.Infof("Taking snapshot")
	m.FCClient.SnapshotVM()
	m.FCClient.StopVM()
	time.Sleep(3 * time.Second)
	m.FCClient.StopFCVMM()
	time.Sleep(3 * time.Second)
}

func (m *MemoryProfiler) LoadSnapshot() {
	log.Infof("Loading snapshot")
	m.FCClient.StartFCVMM()
	time.Sleep(3 * time.Second)
	m.FCClient.RestoreVM()
}

func (m *MemoryProfiler) GetCurrentMemoryPage() int {
	return m.FCClient.PageCount()
}

func (m *MemoryProfiler) GetStableMemoryPage(waitTime, interval int) int {
	time.Sleep(time.Duration(waitTime) * time.Second)
	memoryPage := m.GetCurrentMemoryPage()

	if memoryPage == -1 {
		log.Error("UFFD not running")
		return -1
	}

	for {
		time.Sleep(time.Duration(interval) * time.Second)
		newPage := m.GetCurrentMemoryPage()
		if memoryPage == newPage {
			break
		}
		memoryPage = newPage
	}

	return memoryPage
}

func (m *MemoryProfiler) GracefullyStopFCVM() {
	m.FCClient.StopVM()
	m.GetStableMemoryPage(5, 5)
	log.Infof("Gracefully stopped VM")
	m.FCClient.StopFCVMM()
	log.Infof("Gracefully stopped VMM")
}
