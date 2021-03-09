package nn

import (
	"math"
	"math/rand"
)

func GeneratePopulation(config NeuralNetConfig, mutationRate, mutationScale float64, size int) []*NeuralNet {
	population := make([]*NeuralNet, size)
	for i := 0; i < size; i++ {
		population[i] = NewNetwork(config, mutationRate, mutationScale)
	}

	return population
}

// PoolSelection normalize scores and return model
// indexes selected by the pooling algorithm. Models with
// higher fitness scores will have higher chance of selectoin
func PoolSelection(fitnessScores []float64) []int {
	populationSize := len(fitnessScores)
	selectedIndexes := make([]int, populationSize)

	// Square all scores first
	squared := make([]float64, populationSize)
	for i := 0; i < populationSize; i++ {
		squared[i] = fitnessScores[i] * fitnessScores[i]
		if fitnessScores[i] < 0 {
			squared[i] *= -1
		}
	}

	// Find min and max to normalize scores
	min := math.Inf(1)
	max := math.Inf(-1)
	maxIdx := 0
	for i, score := range squared {
		min = math.Min(min, score)
		if score > max {
			maxIdx = i
			max = score
		}
	}

	// Keep best model
	selectedIndexes[0] = maxIdx

	// All scores are the same
	normalizedScores := make([]float64, populationSize)
	if min == max {
		newScore := 1. / float64(populationSize)
		for i := 0; i < populationSize; i++ {
			normalizedScores[i] = newScore
		}
	} else {
		var sum float64 = 0

		// Subtract min from array
		for i := 0; i < populationSize; i++ {
			normalizedScores[i] = squared[i] - min
			sum += normalizedScores[i]
		}

		// Divide by sum
		for i := 0; i < populationSize; i++ {
			normalizedScores[i] /= sum
		}
	}

	// Pool Selection
	for i := 0; i < populationSize; i++ {
		index := 0
		var cnt float64 = 0

		// Fitness proportionate selection
		r := rand.Float64()
		for cnt < r && index < populationSize {
			cnt += normalizedScores[index]
			index++
		}

		selectedIndexes[i] = index - 1
	}

	return selectedIndexes
}

func CreateNewPopulation(indexes []int, lastGen []*NeuralNet) []*NeuralNet {
	newPopulation := make([]*NeuralNet, len(lastGen))
	for i, index := range indexes {
		newPopulation[i] = lastGen[index].Copy()

		// Do not mutate previous best
		if i != 0 {
			newPopulation[i].Mutate()
		}
	}

	return newPopulation
}
