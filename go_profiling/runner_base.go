package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"
	"fc_benchmark/utils" // Adjust the import path to where utils package is located
)

// Main function for profiling
func RunBase() {
	// Command-line arguments parsing
	language := flag.String("language", "", "Program language")
	experiment := flag.String("expr", "", "Experiment name")
	loop := flag.Int("loop", 1, "Number of experiment loop")
	flag.Parse()

	// Open CSV file for writing
	filePath := fmt.Sprintf("%s/%s_%s_memory.csv", utils.Log_Path, *language, *experiment)
	file, err := os.Create(filePath)
	if err != nil {
		log.Fatalf("Failed to create CSV file: %v", err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Write CSV header
	writer.Write([]string{"base", "tmux"})

	// Loop through experiments
	for i := 0; i < *loop; i++ {
		log.Printf("Loop: %d/%d\n", i+1, *loop)
		memoryPage := []string{}

		// Base case
		profiler, _ := utils.NewMemoryProfiler(*language, *experiment, "echo 'Hello'", "echo 'Hello'")
		profiler.GracefullyStopFCVM()
		profiler.StartNewVM()
		time.Sleep(3 * time.Second)

		profiler.TakeSnapshot()
		profiler.LoadSnapshot()
		memoryPage = append(memoryPage, strconv.Itoa(profiler.GetStableMemoryPage(120, 15)))
		log.Printf("Server memory page: %s\n", memoryPage[0])

		profiler.GracefullyStopFCVM()

		// Tmux case
		profiler, _ = utils.NewMemoryProfiler(*language, *experiment, "echo 'Hello'", "echo 'Hello'")
		profiler.GracefullyStopFCVM()
		profiler.StartNewVM()

		profiler.RunServer()
		profiler.TakeSnapshot()
		profiler.LoadSnapshot()
		memoryPage = append(memoryPage, strconv.Itoa(profiler.GetStableMemoryPage(120, 15)))
		log.Printf("Server memory page: %s\n", memoryPage[1])

		profiler.GracefullyStopFCVM()

		// Write memory pages to CSV
		writer.Write(memoryPage)
	}
}
