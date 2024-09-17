package main

import (
	"encoding/csv"
	"flag"
	"log"
	"os"
	"strconv"
	"time"
	"fc_benchmark/utils" // Adjust the import path to your utils package
)

func RunReap() {
	// Command-line arguments
	language := flag.String("language", "", "Program language")
	experiment := flag.String("expr", "", "Experiment name")
	loop := flag.Int("loop", 1, "Number of experiment loop")
	flag.Parse()

	// CSV file for results
	filePath := utils.Log_Path + "/reap_" + *language + "_" + *experiment + "_memory.csv"
	file, err := os.Create(filePath)
	if err != nil {
		log.Fatalf("Failed to create CSV file: %v", err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Write header
	writer.Write([]string{"Memory"})

	// Loop through experiments
	for i := 0; i < *loop; i++ {
		log.Printf("Loop: %d/%d\n", i+1, *loop)
		memoryPage := []string{}

		profiler, _ := utils.NewMemoryProfiler(*language, *experiment, "", "")
		profiler.GracefullyStopFCVM()
		profiler.StartNewVM()

		profiler.RunServer()
		profiler.WarmupServer(10)
		profiler.TakeSnapshot()
		profiler.LoadSnapshot()

		// Retry until server returns successfully
		for {
			output, err := profiler.InvokeServer()
			if err == nil {
				log.Printf("Server response: %s\n", output)
				break // Exit the loop on success
			}
			
			log.Printf("Error invoking server: %v\n", err)
			log.Println("Retrying ...")
			time.Sleep(5 * time.Second) // Add a small delay before retrying
		}
		log.Println("Response returned")
		memoryPage = append(memoryPage, strconv.Itoa(profiler.GetCurrentMemoryPage()))
		log.Printf("Req memory page: %s\n", memoryPage[0])

		profiler.GracefullyStopFCVM()

		// Write results to CSV
		writer.Write(memoryPage)
	}
}
