package main

import (
	"encoding/csv"
	"log"
	"os"
	"strconv"
	"fc_benchmark/utils"
)

func Run(language string, experiment string, loop int) {
	file, err := os.Create(utils.Log_Path + "/" + language + "_" + experiment + "_memory.csv")
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()
	writer.Write([]string{"Server", "Invoke"})

	for i := 0; i < loop; i++ {
		log.Printf("Loop: %d/%d\n", i+1, loop)
		memoryPage := []string{}

		profiler, _ := utils.NewMemoryProfiler(language, experiment, "", "")
		profiler.GracefullyStopFCVM()
		profiler.StartNewVM()
		profiler.RunServer()
		profiler.WarmupServer(10)
		profiler.TakeSnapshot()
		profiler.LoadSnapshot()

		memoryPage = append(memoryPage, strconv.Itoa(profiler.GetStableMemoryPage(120, 15)))
		log.Printf("Server memory page: %v\n", memoryPage[0])

		profiler.InvokeServer()
		memoryPage = append(memoryPage, strconv.Itoa(profiler.GetStableMemoryPage(30, 15)))
		log.Printf("Req memory page: %v\n", memoryPage[1])

		profiler.GracefullyStopFCVM()
		writer.Write(memoryPage)
	}
}
