# datcreativity-solver

All params are tunable inside the python files themselves, such as the input word list, the output result file and some specific search parameters. 

`tryrandom.py` is the random solver. 
`anneal.py` is both capable of running full-greedy adjusting the word with the lowest score, or running an actual simulated annealing. It can also start from a specified list. 
`optimize.py` is meant to be somewhat of a custom greedy optimizer, but much of this functionality can be replicated by `flag_pure_greedy` in `anneal.py`.

Best result achieved using these scripts: 
As of 8/8/2021: 
Score: 106.41	Percentile: 100.0	alerts, debut, cols, satrap, acres, soldering, relativists

Best in the world:
# https://twitter.com/thomasahle/status/1424178136716095492 109.5
SCore: 109.5 views, reference, inch, niff, partnered, absconds, jujube
