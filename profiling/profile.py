import os
import subprocess
import time
import logging
import argparse
import csv

import utils.constants as constants
import utils.firecracker_vm as fc_client
import utils.uffd as uffd_client



class MemoryProfiler():
    def __init__(self, language: str, experiment: str) -> None:
        self.language = language
        self.experiment = experiment
        self.server_path = os.path.join(constants.WORKLOAD_PATH, language, experiment)
        self.client_path = os.path.join(constants.WORKLOAD_PATH, language, experiment)
        logging.info(f"starting memory profiler for {language} {experiment}")
        
        if self.language == "python":
            self.server_command = f"python3 {self.server_path}/server.py "
            self.client_command = f"python3 {self.server_path}/client.py "
        elif self.language == "cpp":
            self.server_command = f".{self.server_path}/server"
            self.client_command = f".{self.server_path}/client"
        elif self.language == "node":
            self.server_command = f"node {self.server_path}/server.js"
            self.client_command = f"node {self.server_path}/client.js"
        else:
            raise ValueError(f"Unsupported Language")

        self.fc_client = fc_client.FirecrackerVM(f"{self.language}_{self.experiment}")

    def start_new_vm(self) -> None:
        logging.info("Starting new VM")
        self.fc_client.start_fc_vmm()
        self.fc_client.create_vm()
    
    def run_server(self) -> None:
        logging.info("Running server")
        self.fc_client.run_command_on_vm(self.server_command)
    
    def warmup_server(self, loop: None) -> None:
        logging.info("Warming up server")
        if loop == None:
            loop = 10
        
        for i in range(loop):
            subprocess.run(self.client_command, shell=True)
            time.sleep(3)
    
    def invoke_server(self) -> None:
        logging.info("Invoking server")
        subprocess.run(self.client_command, shell=True)
    
    def take_snapshot(self):
        logging.info("Taking snapshot")
        self.fc_client.snapshot_vm()
        self.fc_client.stop_vm()
        self.fc_client.stop_fc_vmm()
    
    def load_snapshot(self):
        logging.info("Loading snapshot")
        self.fc_client.start_fc_vmm()
        self.fc_client.restore_vm()
    
    def get_current_memory_page(self) -> int:
        return self.fc_client.page_count
    
    def get_stable_memory_page(self):
        memory_page = self.get_current_memory_page()
        while True:
            time.sleep(10)
            if memory_page == self.get_current_memory_page():
                break
            memory_page = self.get_current_memory_page()
        return memory_page


def main(language: str, experiment: str, loop: int) -> None:
    with open(f"{constants.LOG_PATH}/{language}_{experiment}_memory.csv", mode='a') as file:
        writer = csv.writer(file)
        writer.writerow(["Server", "Invoke"])
        
        for i in range(loop):
            memory_page = []
            profiler = MemoryProfiler(language, experiment)
            profiler.start_new_vm()
            
            profiler.run_server()
            profiler.warmup_server()
            time.sleep(5)
            profiler.take_snapshot()
            profiler.load_snapshot()
            memory_page.append(profiler.get_stable_memory_page())
            logging.info(f"Memory page: {memory_page[0]}")
            
            profiler.invoke_server()
            memory_page.append(profiler.get_stable_memory_page())
            logging.info(f"Memory page: {memory_page[1] - memory_page[0]}")
            
            profiler.fc_client.stop_vm()
            profiler.fc_client.stop_fc_vmm()
            
            writer.writerow(memory_page)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Profile the code')
    parser.add_argument('--language', '-l', choices= ["python", "cpp", "node"], help='Program language')
    parser.add_argument('--expr', '-e', type=str, help='Experiment name')
    parser.add_argument('--loop', '-n', type=int, help='Number of experiment loop')
    args = parser.parse_args()
    
    main(args.language, args.expr, args.loop)