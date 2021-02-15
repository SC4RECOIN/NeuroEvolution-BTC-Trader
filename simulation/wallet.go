package simulation

type wallet struct {
	startingBalance  float64
	balance          float64
	txDiscountFactor float64
	btcBalance       float64
}

func NewWallet(startingBalance, txFee float64) *wallet {
	return &wallet{
		startingBalance:  startingBalance,
		balance:          startingBalance,
		txDiscountFactor: 1 - txFee,
		btcBalance:       0,
	}
}

func (w *wallet) BuySignal(price float64) {
	if w.btcBalance == 0 {
		w.btcBalance = w.balance / price * w.txDiscountFactor
		w.balance = 0
	}
}

func (w *wallet) SellSignal(price float64) {
	if w.balance == 0 {
		w.balance = w.btcBalance * price * w.txDiscountFactor
		w.btcBalance = 0
	}
}

func (w *wallet) GetReturn() float64 {
	return (w.balance/w.startingBalance - 1) * 100
}
