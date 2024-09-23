package main

import (
	"encoding/csv"
	"flag"
	"os"
	"strconv"
	"time"

	log "github.com/sirupsen/logrus"

	"github.com/JooyoungPark73/fc_benchmark/go_profiling/utils"
)

func main() {
	// Parsing command-line arguments
	language := flag.String("l", "python", "Language")
	experiment := flag.String("e", "helloworld_grpc", "Experiment")
	loop := flag.Int("loop", 1, "Number of loops")
	verbosity := flag.String("verbosity", "info", "Logging verbosity - choose from [info, debug, trace]")
	profiling := flag.String("profiling", "stable", "Profiling type - choose from [stable, reap]")
	flag.Parse()

	log.SetFormatter(&log.TextFormatter{
		TimestampFormat: time.StampMilli,
		FullTimestamp:   true,
	})
	log.SetOutput(os.Stdout)

	switch *verbosity {
	case "debug":
		log.SetLevel(log.DebugLevel)
	case "trace":
		log.SetLevel(log.TraceLevel)
	default:
		log.SetLevel(log.InfoLevel)
	}

	// Call Run function
	switch *profiling {
	case "reap":
		RunReap(*language, *experiment, *loop)
	case "stable":
		Run(*language, *experiment, *loop)
	default:
		log.Fatalf("Invalid profiling type: %s", *profiling)
	}
}

func Run(language string, experiment string, loop int) {
	file, err := os.Create(utils.Log_Path + "/" + language + "_" + experiment + "_memory.csv")
	logger := log.WithFields(log.Fields{"language": language, "experiment": experiment})
	if err != nil {
		logger.Fatal(err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()
	writer.Write([]string{"Server", "Invoke"})

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

		memoryPage = append(memoryPage, strconv.Itoa(profiler.GetStableMemoryPage(120, 15)))
		logger.Infof("Server memory page: %v\n", memoryPage[0])

		output, err := profiler.InvokeServer()
		if err != nil {
			logger.Infof("Error invoking server: %v\n", err)
		} else {
			logger.Infof("Server response: %s\n", output)
		}
		memoryPage = append(memoryPage, strconv.Itoa(profiler.GetStableMemoryPage(30, 15)))
		memoryPage0, err := strconv.Atoi(memoryPage[0])
		if err != nil {
			logger.Fatal(err)
		}
		memoryPage1, err := strconv.Atoi(memoryPage[1])
		if err != nil {
			logger.Fatal(err)
		}

		diff := memoryPage1 - memoryPage0
		logger.Infof("Req memory page: %v\n", diff)

		profiler.GracefullyStopFCVM()
		writer.Write(memoryPage)
	}
}
