# Tensorflow NeuroEvolution BTC Trader
Tensorflow is used to build a population of models that breed and mutate iteratively. The initial population is built given a specified network topology and assigned random weights. For each generation, these weights are randomly mutated and each network is assigned a fitness value based on their performance. A pooling algorithm is used to select models for the next generation and the process is repeated. Models with a higher fitness tend to make it to the next generation where their weights are mutated and idealy create a higher performing generation

### sample output
```
creating population 1
evaluating population....
average score: -2.26%
best score: 148.30%
record score: 148.30%
time: 4.54s
test score: 1.25%
=========================
creating population 2
evaluating population....
average score: 21.37%
best score: 168.31%
record score: 168.31%
time: 2.88s
test score: -11.39%
=========================
creating population 3
evaluating population....
average score: 40.26%
best score: 280.08%
record score: 280.08%
time: 2.83s
test score: -7.51%
...
...
```
