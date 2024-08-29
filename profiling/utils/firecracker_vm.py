import subprocess
import time

import utils.tmux as tmux
import utils.constants as constants
import utils.uffd as uffd



class FirecrackerVM():
    def __init__(self, session_name: str) -> None:
        self.session_name = session_name
        self.tmux_client = tmux.Tmux()
        self.uffd_client = uffd.Uffd()

    def start_fc_vmm(self) -> None:
        subprocess.run(f"bash {constants.SCRIPTS_PATH}/fc_vmm.sh", shell=True)

    def stop_fc_vmm(self) -> None:
        subprocess.run(f"tmux kill-session -t fc_vmm", shell=True)

    def create_vm(self) -> None:
        subprocess.run(f"bash {constants.SCRIPTS_PATH}/run_fc.sh", shell=True)

    def stop_vm(self) -> None:
        subprocess.run(f"ssh -i {constants.UBUBTU_PATH}/ubuntu-22.04.id_rsa root@172.16.0.2 'reboot'", shell=True)
        time.sleep(15)

    def run_command_on_vm(self, command: str) -> None:
        subprocess.run(f"ssh -i {constants.UBUBTU_PATH}/ubuntu-22.04.id_rsa root@172.16.0.2 '{command}'", shell=True)
    
    def run_command_on_vm_tmux(self, command: str) -> None:
        subprocess.run(f"ssh -i {constants.UBUBTU_PATH}/ubuntu-22.04.id_rsa root@172.16.0.2 tmux kill-session -t server", shell=True)
        time.sleep(1)
        subprocess.run(f"ssh -i {constants.UBUBTU_PATH}/ubuntu-22.04.id_rsa root@172.16.0.2 tmux new -s server -d", shell=True)
        time.sleep(1)
        subprocess.run(f"ssh -i {constants.UBUBTU_PATH}/ubuntu-22.04.id_rsa root@172.16.0.2 tmux send -t server '\"{command}\"' ENTER", shell=True)
    
    def snapshot_vm(self) -> None:
        subprocess.run(f"bash {constants.SCRIPTS_PATH}/snapshot_capture.sh", shell=True)
    
    def restore_vm(self) -> None:
        subprocess.run(f"bash {constants.SCRIPTS_PATH}/snapshot_restore.sh", shell=True)
    
    def page_count(self) -> int:
        return self.uffd_client.get_uffd_pages()