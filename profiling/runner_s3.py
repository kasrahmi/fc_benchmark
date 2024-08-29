import argparse
import csv
import logging
import time

import utils.profile as memory_profiler
import utils.constants as constants

def main(language: str, experiment: str, loop: int) -> None:
    with open(f"{constants.LOG_PATH}/{language}_{experiment}_memory.csv", mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["get", "put", "get_put", "init", "init_get", "init_get_put"])
        
        for i in range(loop):
            logging.info(f"Loop: {i+1}/{loop}")
            memory_page = []
            
            # GET
            profiler = memory_profiler.MemoryProfiler(language, experiment, f"python3 /root/workload/python/s3/s3_get.py --bucket jyp-benchmark --outdir /root/workload/python/s3/temp/sample_16B.txt --object sample_16B.txt", f"echo 'Hello'")
            profiler.fc_client.stop_vm()
            profiler.fc_client.stop_fc_vmm()
            profiler.start_new_vm()
            
            profiler.run_server()
            time.sleep(30)
            profiler.take_snapshot()
            profiler.load_snapshot()
            memory_page.append(profiler.get_stable_memory_page(30, 15))
            logging.info(f"Server memory page: {memory_page}")
            
            profiler.fc_client.stop_vm()
            profiler.fc_client.stop_fc_vmm()
            
            # PUT
            profiler = memory_profiler.MemoryProfiler(language, experiment, f"python3 /root/workload/python/s3/s3_put.py --bucket jyp-benchmark --filename /root/workload/payload/sample_16B.txt --object sample_16B.txt", f"echo 'Hello'")
            profiler.start_new_vm()
            
            profiler.run_server()
            time.sleep(30)
            profiler.take_snapshot()
            profiler.load_snapshot()
            memory_page.append(profiler.get_stable_memory_page(30, 15))
            logging.info(f"Server memory page: {memory_page}")
            
            profiler.fc_client.stop_vm()
            profiler.fc_client.stop_fc_vmm()
            

            # GET PUT
            profiler = memory_profiler.MemoryProfiler(language, experiment, f"python3 /root/workload/python/s3/s3_get_put.py --bucket jyp-benchmark --outdir /root/workload/python/s3/temp/sample_16B.txt --filename /root/workload/payload/sample_16B.txt --object sample_16B.txt", f"echo 'Hello'")
            profiler.fc_client.stop_vm()
            profiler.fc_client.stop_fc_vmm()
            profiler.start_new_vm()
            
            profiler.run_server()
            time.sleep(30)
            profiler.take_snapshot()
            profiler.load_snapshot()
            memory_page.append(profiler.get_stable_memory_page(30, 15))
            logging.info(f"Server memory page: {memory_page}")
            
            profiler.fc_client.stop_vm()
            profiler.fc_client.stop_fc_vmm()
            
            
            # INIT Only
            profiler = memory_profiler.MemoryProfiler(language, experiment, f"python3 /root/workload/python/s3/s3_init.py", f"echo 'Hello'")
            profiler.fc_client.stop_vm()
            profiler.fc_client.stop_fc_vmm()
            profiler.start_new_vm()
            
            profiler.run_server()
            profiler.take_snapshot()
            profiler.load_snapshot()
            memory_page.append(profiler.get_stable_memory_page(30, 15))
            logging.info(f"Server memory page: {memory_page}")
            
            profiler.fc_client.stop_vm()
            profiler.fc_client.stop_fc_vmm()
            
            
            # INIT GET
            profiler = memory_profiler.MemoryProfiler(language, experiment, f"python3 /root/workload/python/s3/s3_init_get.py --bucket jyp-benchmark --outdir /root/workload/python/s3/temp/sample_16B.txt --object sample_16B.txt", f"echo 'Hello'")
            profiler.fc_client.stop_vm()
            profiler.fc_client.stop_fc_vmm()
            profiler.start_new_vm()
            
            profiler.run_server()
            time.sleep(30)
            profiler.take_snapshot()
            profiler.load_snapshot()
            memory_page.append(profiler.get_stable_memory_page(30, 15))
            logging.info(f"Server memory page: {memory_page}")
            
            profiler.fc_client.stop_vm()
            profiler.fc_client.stop_fc_vmm()
            
            # INIT GET PUT
            profiler = memory_profiler.MemoryProfiler(language, experiment, f"python3 /root/workload/python/s3/s3_init_get_put.py --bucket jyp-benchmark --outdir /root/workload/python/s3/temp/sample_16B.txt --filename /root/workload/payload/sample_16B.txt --object sample_16B.txt", f"echo 'Hello'")
            profiler.fc_client.stop_vm()
            profiler.fc_client.stop_fc_vmm()
            profiler.start_new_vm()
            
            profiler.run_server()
            time.sleep(30)
            profiler.take_snapshot()
            profiler.load_snapshot()
            memory_page.append(profiler.get_stable_memory_page(30, 15))
            logging.info(f"Server memory page: {memory_page}")
            
            profiler.fc_client.stop_vm()
            profiler.fc_client.stop_fc_vmm()
            
            writer.writerow(memory_page)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Profile the code')
    parser.add_argument('--language', '-l', type=str , help='Program language')
    parser.add_argument('--expr', '-e', type=str, help='Experiment name')
    parser.add_argument('--loop', '-n', type=int, help='Number of experiment loop')
    args = parser.parse_args()
    
    main(args.language, args.expr, args.loop)