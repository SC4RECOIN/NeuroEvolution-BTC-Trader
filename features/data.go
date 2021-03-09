package features

import (
	"context"
	"fmt"
	"strconv"
	"time"

	"github.com/adshao/go-binance/v2"
)

func LoadHistoricalData(start int64) ([]float64, []float64, []float64, []float64, error) {
	const minute = 60000
	client := binance.NewClient("", "")
	var end int64 = time.Now().Unix() * 1000
	var closes, volumes, highs, lows []float64

	parseFloat := func(value string) float64 {
		floatValue, _ := strconv.ParseFloat(value, 32)
		return floatValue
	}

	fmt.Println("Fetching historical data")
	for start < end {
		fmt.Println(start)
		klines, err := client.NewKlinesService().
			Symbol("BTCUSDT").
			Interval("15m").
			StartTime(start).
			Do(context.Background())

		if err != nil {
			return closes, volumes, highs, lows, err
		}

		// Parse values from struct
		for _, kline := range klines {
			closes = append(closes, parseFloat(kline.Close))
			volumes = append(volumes, parseFloat(kline.Volume))
			highs = append(highs, parseFloat(kline.High))
			lows = append(lows, parseFloat(kline.Low))
		}

		start = klines[len(klines)-1].OpenTime + minute*15
	}

	fmt.Printf("Returning %d candles\n", len(closes))
	return closes, volumes, highs, lows, nil
}
