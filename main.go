package main

import (
	"fmt"
	"log"
	"math"
	"sync"
	"time"

	"./features"
	"./nn"
	"./simulation"
)

func main() {
	// Load candles and TA
	candleStart := time.Now().AddDate(0, 0, -16).Unix() * 1000
	closes, volumes, highs, lows, err := features.LoadHistoricalData(candleStart)
	if err != nil {
		panic(err)
	}

	inputs, inputsTest := features.CalcTA(closes, highs, lows, volumes, 0.05)

	// Split closes to match x and x_test
	rows, _ := inputs.Dims()
	closesTest := closes[rows:]
	closes = closes[:rows]

	benchmark := (closes[len(closes)-1]/closes[0] - 1) * 100
	benchTest := (closes[len(closesTest)-1]/closesTest[0] - 1) * 100
	_, c := inputs.Dims()

	concurrentSims := 3
	episodes := 100000
	populationSize := 350
	decayInterval := 50
	config := nn.NeuralNetConfig{
		InputNeurons:  c,
		HiddenNeurons: 32,
		HiddenLayers:  2,
		OutputNeurons: 2,
	}

	population := nn.GeneratePopulation(config, 0.15, 0.1, populationSize)

	start := time.Now()
	for i := 0; i < episodes; i++ {
		// Scale back mutation
		if i%decayInterval == 0 {
			for _, model := range population {
				mutationRate := math.Max(0.02, model.MutationRate-0.005)
				mutationScale := math.Max(0.01, model.MutationRate-0.005)
				model.SetMutation(mutationRate, mutationScale)
			}
		}

		fitness := make([]float64, populationSize)
		wg := &sync.WaitGroup{}

		// Run all sims in goroutine and wait
		for j, model := range population {
			wg.Add(1)
			go simulation.RunSimulation(model, inputs, &closes, &fitness[j], wg)

			if j%concurrentSims == 0 {
				wg.Wait()
			}
		}

		wg.Wait()

		nextGenIndexes := nn.PoolSelection(fitness)
		population = nn.CreateNewPopulation(nextGenIndexes, population)

		max := math.Inf(-1)
		maxIdx := 0
		for j, score := range fitness {
			if score > max {
				maxIdx = j
				max = score
			}
		}

		// Test best model on test data
		wg.Add(1)
		var testResult float64
		simulation.RunSimulation(population[maxIdx], inputsTest, &closesTest, &testResult, wg)

		elapsed := time.Since(start)
		fmt.Printf("%s\t%s\tEpisode: %06d  Return: %.3f%%\tBenchmark: %.3f%%\tTest Return: %.3f%%\tBenchmark Test: %.3f%%\n",
			time.Now().Format("2006-01-02 15:04:05"),
			elapsed,
			i,
			max,
			benchmark,
			testResult,
			benchTest,
		)
	}
	elapsed := time.Since(start)
	log.Printf("Execution time %s", elapsed)
}
