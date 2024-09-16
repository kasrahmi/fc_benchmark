package main

import (
	"encoding/csv"
	"log"
	"os"
	"time"
	"strconv"
	"fc_benchmark/utils"
)

func RunS3(language string, experiment string, loop int) {
	file, err := os.Create(utils.Log_Path + "/" + language + "_" + experiment + "_memory.csv")
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()
	writer.Write([]string{"get", "put", "get_put", "init", "init_get", "init_get_put"})

	for i := 0; i < loop; i++ {
		log.Printf("Loop: %d/%d\n", i+1, loop)
		memoryPage := []string{}

		// GET
		profiler, _ := utils.NewMemoryProfiler(language, experiment, "python3 /root/workload/python/s3/s3_get.py --bucket jyp-benchmark --outdir /root/workload/python/s3/temp/sample_16B.txt --object sample_16B.txt", "echo 'Hello'")
		profiler.FCClient.StopVM()
		profiler.FCClient.StopFCVMM()
		profiler.StartNewVM()
		profiler.RunServer()
		time.Sleep(30 * time.Second)
		profiler.TakeSnapshot()
		profiler.LoadSnapshot()
		
		// Call the method on the profiler instance
		memoryPage = append(memoryPage, strconv.Itoa(profiler.GetStableMemoryPage(30, 15)))

		// Continue for PUT, GET_PUT, etc.
		// (Repeat the logic similar to the GET section)
		profiler.FCClient.StopVM()
		profiler.FCClient.StopFCVMM()

		writer.Write(memoryPage)
	}
}
