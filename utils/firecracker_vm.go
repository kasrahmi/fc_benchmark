package utils

import (
	"fmt"
    "log"
    "os/exec"
    "time"
)

// FirecrackerVM struct to manage the Firecracker VM
type FirecrackerVM struct {
    SessionName  string
    TmuxClient   Tmux
    UffdClient   Uffd
}

// StartFCVMM starts the Firecracker VMM by running the fc_vmm.sh script
func (f *FirecrackerVM) StartFCVMM() {
    log.Println("Starting Firecracker VMM")
    cmd := exec.Command("bash", ScriptsPath+"/fc_vmm.sh")
    if err := cmd.Run(); err != nil {
        log.Fatalf("Failed to start VMM: %v", err)
    }
}

// StopFCVMM stops the Firecracker VMM by killing the tmux session
func (f *FirecrackerVM) StopFCVMM() {
    log.Println("Stopping Firecracker VMM")
    cmd := exec.Command("tmux", "kill-session", "-t", "fc_vmm")
    if err := cmd.Run(); err != nil {
        log.Fatalf("Failed to stop VMM: %v", err)
    }
}

// CreateVM runs the script to create the Firecracker VM
func (f *FirecrackerVM) CreateVM() {
    log.Println("Creating Firecracker VM")
    cmd := exec.Command("bash", ScriptsPath+"/run_fc.sh")
    if err := cmd.Run(); err != nil {
        log.Fatalf("Failed to create VM: %v", err)
    }
}

// StopVM stops the Firecracker VM by sending a reboot command via SSH
func (f *FirecrackerVM) StopVM() {
    log.Println("Stopping Firecracker VM")
    cmd := exec.Command("ssh", "-i", UbuntuPath+"/ubuntu-22.04.id_rsa", "root@192.168.0.2", "reboot")
    if err := cmd.Run(); err != nil {
        log.Fatalf("Failed to stop VM: %v", err)
    }
    time.Sleep(15 * time.Second)
}

// RunCommandOnVM runs a command inside the VM via SSH
func (f *FirecrackerVM) RunCommandOnVM(command string) {
    log.Printf("Running command on VM: %s", command)
    cmd := exec.Command("ssh", "-i", UbuntuPath+"/ubuntu-22.04.id_rsa", "root@192.168.0.2", command)
    if err := cmd.Run(); err != nil {
        log.Fatalf("Failed to run command on VM: %v", err)
    }
}

// RunCommandOnVMTmux runs a command in tmux on the VM via SSH
func (f *FirecrackerVM) RunCommandOnVMTmux(command string) {
    log.Printf("Running tmux command on VM: %s", command)
    exec.Command("ssh", "-i", UbuntuPath+"/ubuntu-22.04.id_rsa", "root@192.168.0.2", "tmux kill-session -t server").Run()
    time.Sleep(1 * time.Second)
    exec.Command("ssh", "-i", UbuntuPath+"/ubuntu-22.04.id_rsa", "root@192.168.0.2", "tmux new -s server -d").Run()
    time.Sleep(1 * time.Second)
    exec.Command("ssh", "-i", UbuntuPath+"/ubuntu-22.04.id_rsa", "root@192.168.0.2", "tmux send -t server", fmt.Sprintf(`"%s"`, command), "ENTER").Run()
}

// SnapshotVM captures a snapshot of the VM using a script
func (f *FirecrackerVM) SnapshotVM() {
    log.Println("Capturing VM snapshot")
    cmd := exec.Command("bash", ScriptsPath+"/snapshot_capture.sh")
    if err := cmd.Run(); err != nil {
        log.Fatalf("Failed to capture snapshot: %v", err)
    }
}

// RestoreVM restores the VM from a snapshot using a script
func (f *FirecrackerVM) RestoreVM() {
    log.Println("Restoring VM snapshot")
    cmd := exec.Command("bash", ScriptsPath+"/snapshot_restore.sh")
    if err := cmd.Run(); err != nil {
        log.Fatalf("Failed to restore snapshot: %v", err)
    }
}

// PageCount retrieves the current UFFD page count using the Uffd client
func (f *FirecrackerVM) PageCount() int {
	num, _ := f.UffdClient.GetUffdPages()
    return num
}
