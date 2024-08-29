import argparse
import csv
import logging
import time

import utils.profile as memory_profiler
import utils.constants as constants

def main(language: str, experiment: str, loop: int) -> None:
    with open(f"{constants.LOG_PATH}/{language}_{experiment}_memory.csv", mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["base", "tmux"])
        
        for i in range(loop):
            logging.info(f"Loop: {i+1}/{loop}")
            memory_page = []
            
            # Base
            profiler = memory_profiler.MemoryProfiler(language, experiment, f"echo 'Hello'", f"echo 'Hello'")
            profiler.gracefuly_stop_fc_vm()
            profiler.start_new_vm()
            time.sleep(3)
            
            profiler.take_snapshot()
            profiler.load_snapshot()
            memory_page.append(profiler.get_stable_memory_page(120, 15))
            logging.info(f"Server memory page: {memory_page[0]}")
            
            profiler.gracefuly_stop_fc_vm()
            
            # Tmux
            profiler = memory_profiler.MemoryProfiler(language, experiment, f"echo 'Hello'", f"echo 'Hello'")
            profiler.gracefuly_stop_fc_vm()
            profiler.start_new_vm()
            
            profiler.run_server()
            profiler.take_snapshot()
            profiler.load_snapshot()
            memory_page.append(profiler.get_stable_memory_page(120, 15))
            logging.info(f"Server memory page: {memory_page[1]}")
            
            profiler.gracefuly_stop_fc_vm()
            
            writer.writerow(memory_page)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Profile the code')
    parser.add_argument('--language', '-l', type=str , help='Program language')
    parser.add_argument('--expr', '-e', type=str, help='Experiment name')
    parser.add_argument('--loop', '-n', type=int, help='Number of experiment loop')
    args = parser.parse_args()
    
    main(args.language, args.expr, args.loop)