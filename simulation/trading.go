package simulation

import (
	"log"
	"sync"

	"../nn"
	"gonum.org/v1/gonum/mat"
)

func RunSimulation(model *nn.NeuralNet, inputs *mat.Dense, closes *[]float64, result *float64, wg *sync.WaitGroup) {
	defer wg.Done()
	wallet := NewWallet(10000.0, 0.0005)
	prices := *closes

	modelOutputs, err := model.Predict(inputs)
	if err != nil {
		log.Fatal("Model outputs returned error")
		*result = 0
		return
	}

	for i := 0; i < len(prices); i++ {
		// Buy or sell signal
		if modelOutputs.At(i, 0) > modelOutputs.At(i, 1) {
			wallet.BuySignal(prices[i])
		} else {
			wallet.SellSignal(prices[i])
		}
	}

	// Close any positions
	wallet.SellSignal(prices[len(prices)-1])
	*result = wallet.GetReturn()
}
