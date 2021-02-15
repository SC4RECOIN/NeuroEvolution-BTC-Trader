package features

import (
	"math"

	"github.com/markcheno/go-talib"
	"github.com/pa-m/sklearn/preprocessing"
	"gonum.org/v1/gonum/mat"
)

func CalcTA(closes, highs, lows, volumes []float64, testSize float64) (*mat.Dense, *mat.Dense) {
	var values []float64
	signalCnt := 0

	// Money Flow Index (invert signal)
	mfi := talib.Mfi(highs, lows, closes, volumes, 16)
	for i := 0; i < len(mfi); i++ {
		mfi[i] = 100 - mfi[i]
	}
	values = append(values, mfi...)
	signalCnt++

	// MACD histogram
	_, _, hist := talib.Macd(closes, 12, 24, 9)
	values = append(values, hist...)
	signalCnt++

	// Moving average (diff from close)
	ma := talib.Sma(closes, 175)
	for i := 0; i < len(ma); i++ {
		ma[i] = closes[i] - ma[i]
	}
	values = append(values, ma...)
	signalCnt++

	// BB
	upper, _, lower := talib.BBands(closes, 40, 2, 2, 0)
	for i := 0; i < len(upper); i++ {
		upper[i] = closes[i] - upper[i]
		lower[i] = closes[i] - lower[i]
	}
	values = append(values, upper...)
	values = append(values, lower...)
	signalCnt += 2

	// CCI (invert)
	cci := talib.Cci(highs, lows, closes, 17)
	for i := 0; i < len(cci); i++ {
		cci[i] = -1 * cci[i]
	}
	values = append(values, cci...)
	signalCnt++

	transposed := mat.NewDense(signalCnt, len(closes), values).T()
	denseInputs := mat.DenseCopyOf(transposed)

	// Split test and train
	nSamples, nFeatures := denseInputs.Dims()
	splitIndex := nSamples / 2
	xTrain := mat.NewDense(splitIndex, nFeatures, nil)
	xTest := mat.NewDense(nSamples-splitIndex, nFeatures, nil)

	for i := 0; i < nSamples; i++ {
		if i < splitIndex {
			mat.Row(xTrain.RawRowView(i), i, denseInputs)
		} else {
			mat.Row(xTest.RawRowView(i-splitIndex), i, denseInputs)
		}
	}

	// Scale the inputs
	scaler := preprocessing.NewStandardScaler()
	scaler.Fit(xTrain, nil)
	xTrain, _ = scaler.Transform(xTrain, nil)
	xTest, _ = scaler.Transform(xTest, nil)

	return xTrain, xTest
}

func MinMaxScale(inputs []float64) []float64 {
	min := math.Inf(1)
	max := math.Inf(-1)
	for i := 0; i < len(inputs); i++ {
		min = math.Min(inputs[i], min)
		max = math.Max(inputs[i], max)
	}
	max -= min

	scaled := make([]float64, len(inputs))
	for i := 0; i < len(inputs); i++ {
		scaled[i] = (inputs[i] - min) / max
	}

	return scaled
}
