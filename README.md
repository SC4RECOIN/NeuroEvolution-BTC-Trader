# NeuroEvolution BTC Trader

The goal of this project was to create a model that would trade on technicals through neuroevolution. The initial population is built given a specified network topology and assigned random weights. For each generation, these weights are randomly mutated and each network is assigned a fitness value based on its performance. A pooling algorithm is then used to select models for the next generation and the process is repeated. Models with a higher fitness tend to make it to the next generation where their weights are mutated and ideally create a higher performing generation.

See [python branch](https://github.com/SC4RECOIN/NeuroEvolution-BTC-Trader/tree/python) for original implementation
