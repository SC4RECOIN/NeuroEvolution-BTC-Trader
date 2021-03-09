package nn

import (
	"math"
	"math/rand"
	"time"

	"gonum.org/v1/gonum/mat"
)

type NeuralNet struct {
	Config        NeuralNetConfig
	WHidden       []*mat.Dense
	BHidden       []*mat.Dense
	WOut          *mat.Dense
	BOut          *mat.Dense
	MutationRate  float64
	MutationScale float64
}

type NeuralNetConfig struct {
	InputNeurons  int
	OutputNeurons int
	HiddenNeurons int
	HiddenLayers  int
}

func newLayer(inputs, outputs int) (*mat.Dense, *mat.Dense) {
	weights := mat.NewDense(inputs, outputs, nil)
	bias := mat.NewDense(1, outputs, nil)

	// Initialize
	for _, param := range [][]float64{
		weights.RawMatrix().Data,
		bias.RawMatrix().Data,
	} {
		for i := range param {
			param[i] = rand.NormFloat64()
		}
	}

	return weights, bias
}

// NewNetwork initializes a new neural network.
func NewNetwork(config NeuralNetConfig, mutationRate, mutationScale float64) *NeuralNet {
	rand.Seed(time.Now().UnixNano())

	net := NeuralNet{
		Config:        config,
		MutationRate:  mutationRate,
		MutationScale: mutationScale,
	}

	// Layers
	net.WHidden = make([]*mat.Dense, config.HiddenLayers)
	net.BHidden = make([]*mat.Dense, config.HiddenLayers)

	// Inputs
	net.WHidden[0], net.BHidden[0] = newLayer(net.Config.InputNeurons, net.Config.HiddenNeurons)

	// Hidden layers
	for i := 1; i < config.HiddenLayers; i++ {
		net.WHidden[i], net.BHidden[i] = newLayer(net.Config.HiddenNeurons, net.Config.HiddenNeurons)
	}

	// Outputs
	net.WOut, net.BOut = newLayer(net.Config.HiddenNeurons, net.Config.OutputNeurons)

	return &net
}

func (net *NeuralNet) Mutate() {
	for _, layer := range net.WHidden {
		for i, _ := range layer.RawMatrix().Data {
			// Mutate if above set rate
			if rand.Float64() < net.MutationRate {
				layer.RawMatrix().Data[i] += rand.NormFloat64() * net.MutationScale
			}
		}
	}

	// Mutate output layer too
	for i, _ := range net.WOut.RawMatrix().Data {
		if rand.Float64() < net.MutationRate {
			net.WOut.RawMatrix().Data[i] += rand.NormFloat64() * net.MutationScale
		}
	}
}

func (net *NeuralNet) Copy() *NeuralNet {
	copy := NeuralNet{
		Config:        net.Config,
		MutationRate:  net.MutationRate,
		MutationScale: net.MutationScale,
	}

	// Layers
	copy.WHidden = make([]*mat.Dense, net.Config.HiddenLayers)
	copy.BHidden = make([]*mat.Dense, net.Config.HiddenLayers)

	// Copy weights
	for i := 0; i < net.Config.HiddenLayers; i++ {
		copy.WHidden[i] = mat.DenseCopyOf(net.WHidden[i])
		copy.BHidden[i] = mat.DenseCopyOf(net.BHidden[i])
	}

	// Outputs
	copy.WOut = mat.DenseCopyOf(net.WOut)
	copy.BOut = mat.DenseCopyOf(net.BOut)

	return &copy
}

func (net *NeuralNet) SetMutation(mutationRate, mutationScale float64) {
	net.MutationRate = mutationRate
	net.MutationScale = mutationScale
}

func (net *NeuralNet) Predict(x *mat.Dense) (*mat.Dense, error) {
	applyActivation := func(_, _ int, v float64) float64 { return leakyRelu(v) }

	// Inputs
	hiddenLayerInput := new(mat.Dense)
	hiddenLayerInput.Mul(x, net.WHidden[0])
	addBHidden := func(_, col int, v float64) float64 { return v + net.BHidden[0].At(0, col) }
	hiddenLayerInput.Apply(addBHidden, hiddenLayerInput)

	inputActivations := new(mat.Dense)
	inputActivations.Apply(applyActivation, hiddenLayerInput)

	// Hidden layers
	last := inputActivations
	for i := 1; i < len(net.WHidden); i++ {
		hiddenLayerInput := new(mat.Dense)
		hiddenLayerInput.Mul(last, net.WHidden[i])

		addBHidden := func(_, col int, v float64) float64 { return v + net.BHidden[i].At(0, col) }
		hiddenLayerInput.Apply(addBHidden, hiddenLayerInput)

		hiddenLayerActivations := new(mat.Dense)
		hiddenLayerActivations.Apply(applyActivation, hiddenLayerInput)

		last = hiddenLayerActivations
	}

	// Output
	outputLayerInput := new(mat.Dense)
	outputLayerInput.Mul(last, net.WOut)
	addBOut := func(_, col int, v float64) float64 { return v + net.BOut.At(0, col) }
	outputLayerInput.Apply(addBOut, outputLayerInput)

	output := new(mat.Dense)
	output.Apply(applyActivation, outputLayerInput)

	return output, nil
}

func sigmoid(x float64) float64 {
	return 1.0 / (1.0 + math.Exp(-x))
}

func relu(x float64) float64 {
	if x > 0 {
		return x
	}
	return 0
}

func leakyRelu(x float64) float64 {
	if x > 0 {
		return x
	}
	return 0.01 * x
}
