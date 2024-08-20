import subprocess
import tmux
import time
import profiling.utils.constants as constants
import uffd



class FirecrackerVM():
    def __init__(self, session_name: str) -> None:
        self.session_name = session_name + "_fc_vmm"
        self.tmux_client = tmux.Tmux
        self.uffd_client = uffd.Uffd

    def start_fc_vmm(self) -> None:
        self.tmux_client.create_session(self.session_name)
        time.sleep(1)
        self.tmux_client.run_command_in_session(self.session_name, f"sudo {constants.FC_VMM_PATH}")

    def stop_fc_vmm(self) -> None:
        self.tmux_client.kill_session(self.session_name)

    def create_vm(self) -> None:
        subprocess.run(f"sudo {constants.SCRIPTS_PATH}/run_fc.sh", shell=True)

    def stop_vm(self) -> None:
        subprocess.run(f"ssh -i {constants.UBUBTU_PATH}/ubuntu-22.04.id_rsa root@172.16.0.2 'reboot'", shell=True)

    def run_command_on_vm(self, command: str) -> None:
        subprocess.run(f"ssh -i {constants.UBUBTU_PATH}/ubuntu-22.04.id_rsa root@172.16.0.2 '{command}'", shell=True)
    
    def snapshot_vm(self) -> None:
        subprocess.run(f"sudo {constants.SCRIPTS_PATH}/snapshot_capture.sh", shell=True)
    
    def restore_vm(self) -> None:
        self.uffd_client.create_uffd_session(self.session_name)
        subprocess.run(f"sudo {constants.SCRIPTS_PATH}/snapshot_restore.sh", shell=True)
    
    def page_count(self) -> int:
        return self.uffd_client.get_uffd_pages(self.session_name)