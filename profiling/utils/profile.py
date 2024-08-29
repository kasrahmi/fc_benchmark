import os
import subprocess
import time
import logging

import utils.constants as constants
import utils.firecracker_vm as fc_client



class MemoryProfiler():
    def __init__(self, language: str, experiment: str, server_command: (str|None), client_command: (str|None)) -> None:
        self.language = language
        self.experiment = experiment
        self.server_path = os.path.join(f"/root/workload", language, experiment)
        self.client_path = os.path.join(constants.WORKLOAD_PATH, language, experiment)
        logging.info(f"starting memory profiler for {language} {experiment}")
        
        if server_command == None and client_command == None:
            if self.language == "python":
                self.server_command = f"python3 {self.server_path}/server.py"
                self.client_command = f"python3 {self.client_path}/client.py"
            elif self.language == "cpp":
                self.server_command = f"{self.server_path}/server"
                self.client_command = f"{self.client_path}/client"
            elif self.language == "node":
                self.server_command = f"node {self.server_path}/server.js"
                self.client_command = f"node {self.client_path}/client.js"
            else:
                raise ValueError(f"Unsupported Language")
        elif server_command != None and client_command != None:
            self.server_command = server_command
            self.client_command = client_command
        
        else:
            raise ValueError(f"Enter both server and client command")

        self.fc_client = fc_client.FirecrackerVM(f"{self.language}_{self.experiment}")
    
    def start_new_vm(self) -> None:
        logging.info("Starting new VM")
        self.fc_client.start_fc_vmm()
        time.sleep(3)
        self.fc_client.create_vm()
        time.sleep(3)
    
    def run_server(self) -> None:
        logging.info(f"Running server: {self.server_command}")
        self.fc_client.run_command_on_vm_tmux(self.server_command)
        time.sleep(3)
    
    def warmup_server(self, loop: None) -> None:
        logging.info("Warming up server")
        if loop == None:
            loop = 10
        success_count = 1
        fail_count = 1
        while True:
            print(f"Warming up {success_count}/{loop}")
            return_code = subprocess.run(self.client_command, shell=True).returncode
            if return_code == 0:
                success_count += 1
            else:
                fail_count += 1
            if success_count == loop or fail_count == loop:
                break
            time.sleep(5)
    
    def invoke_server(self) -> None:
        logging.info("Invoking server")
        return_code = subprocess.run(self.client_command, shell=True).returncode
        return return_code
    
    def take_snapshot(self):
        logging.info("Taking snapshot")
        self.fc_client.snapshot_vm()
        self.fc_client.stop_vm()
        time.sleep(3)
        self.fc_client.stop_fc_vmm()
        time.sleep(3)
    
    def load_snapshot(self):
        logging.info("Loading snapshot")
        self.fc_client.start_fc_vmm()
        time.sleep(3)
        self.fc_client.restore_vm()
    
    def get_current_memory_page(self) -> int:
        return self.fc_client.page_count()
    
    def get_stable_memory_page(self, wait_time: int, interval: int) -> int:
        time.sleep(wait_time)
        memory_page = self.get_current_memory_page()
        if memory_page == -1:
            logging.info("uffd not running")
            return -1
        while True:
            time.sleep(interval)
            if memory_page == self.get_current_memory_page():
                break
            memory_page = self.get_current_memory_page()
        return memory_page

    def gracefuly_stop_fc_vm(self) -> None:
        self.fc_client.stop_vm()
        self.get_stable_memory_page(5, 5)
        logging.info("Gracefully stopped VM")
        self.fc_client.stop_fc_vmm()
        logging.info("Gracefully stopped VMM")