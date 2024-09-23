package main

import (
	"encoding/csv"
	"os"
	"strconv"

	log "github.com/sirupsen/logrus"

	"github.com/JooyoungPark73/fc_benchmark/go_profiling/utils"
)

func RunReap(language string, experiment string, loop int) {
	filePath := utils.Log_Path + "/reap_" + language + "_" + experiment + "_memory.csv"
	file, err := os.Create(filePath)
	logger := log.WithFields(log.Fields{"language": language, "experiment": experiment})

	if err != nil {
		logger.Fatalf("Failed to create CSV file: %v", err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Write header
	writer.Write([]string{"Memory"})

	// Loop through experiments
	for i := 0; i < loop; i++ {
		logger.Infof("Loop: %d/%d\n", i+1, loop)
		memoryPage := []string{}

		profiler, _ := utils.NewMemoryProfiler(language, experiment, "", "")
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
				logger.Infof("Server response: %s\n", output)
				break // Exit the loop on success
			}

			logger.Infof("Error invoking server: %v\n", err)
			logger.Infof("Retrying ...")
		}
		logger.Infof("Response returned")
		memoryPage = append(memoryPage, strconv.Itoa(profiler.GetCurrentMemoryPage()))
		logger.Infof("Req memory page: %s\n", memoryPage[0])

		profiler.GracefullyStopFCVM()

		// Write results to CSV
		writer.Write(memoryPage)
	}
}
