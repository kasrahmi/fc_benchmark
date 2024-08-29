import argparse
import csv
import logging
import time

import utils.profile as memory_profiler
import utils.constants as constants

def main(language: str, experiment: str, loop: int) -> None:
    with open(f"{constants.LOG_PATH}/reap_{language}_{experiment}_memory.csv", mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Memory"])
        
        for i in range(loop):
            logging.info(f"Loop: {i+1}/{loop}")
            memory_page = []
            profiler = memory_profiler.MemoryProfiler(language, experiment, None, None)
            profiler.gracefuly_stop_fc_vm()
            profiler.start_new_vm()
            
            profiler.run_server()
            profiler.warmup_server(10)
            profiler.take_snapshot()
            profiler.load_snapshot()
            
            while True:
                return_code = profiler.invoke_server()
                if return_code == 0:
                    break
                logging.info("Retrying ...")
            logging.info("response returned")
            memory_page.append(profiler.get_current_memory_page())
            logging.info(f"Req memory page: {memory_page[0]}")
            
            profiler.gracefuly_stop_fc_vm()
            
            writer.writerow(memory_page)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Profile the code')
    parser.add_argument('--language', '-l', choices= ["python", "cpp", "node"], help='Program language')
    parser.add_argument('--expr', '-e', type=str, help='Experiment name')
    parser.add_argument('--loop', '-n', type=int, help='Number of experiment loop')
    args = parser.parse_args()
    
    main(args.language, args.expr, args.loop)