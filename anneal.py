import requests
from bs4 import BeautifulSoup
import random
import re
import time
import math

words = []
# '/usr/share/dict/words' leads to invalid results 
# FILE = '/usr/share/dict/words' # mostly errors in spelling
# FILE = 'data/nouns-91k.txt'
# FILE = 'data/nouns-6k.txt'
# FILE = 'data/nouns-sorted.txt' # too small
# FILE = 'data/nounlist-large.txt' #7k
FILE = 'data/corncob_lowercase.txt'
# RESULTS = 'results.csv'
BATCH_SIZE = 10
ATTEMPTS = 1000
NUM_WORDS = 7
OUTPUT = 'anneal.csv'
# Mutate the word with the lowest score only
flag_select_lowest_row = True
# Mutate two words at a time instead of just one
mutate_two = False	
# Switch this to false to make Simulated Annealing do a strict climb. Along with flag_select_lowest_row=True, this is pure greedy
flag_pure_greedy = True
k_max = 10000
start_words = 'denudes, versification, condoles, tablespoons, gear, lyrics, published'



with open(FILE, 'r') as f:
	words = [x.strip() for x in f.read().split('\n')]


words = [w for w in  words if w.lower() == w]
# Parsing
PRECENTILE_REGEX = re.compile('higher than ([0-9\.]{,})%')
def parse(soup):
	errors = soup.findAll('span', {'class': 'error'})
	if len(errors):
		etexts = [e.text for e in errors]
		# import pdb; pdb.set_trace()
		return None, None, None, etexts
	headertext = soup.find('h2').text
	if headertext == 'Web server is returning an unknown error':
		return None, None, None, ['web server error']
	try:
		score = soup.find('h2').find('span').text
		percentile = re.search(PRECENTILE_REGEX, soup.find('h2').text).group(1)
		table = [[w.text for w in row.findAll('td')] for row in soup.find('table').findAll('tr')[1:]]
	except e:
		import pdb; pdb.set_trace()
	return score, percentile, table, None

def get_results(selection_inp):
	selection = [s for s in selection_inp]
	# Append 3 random misspelt words to make the API happy even though they're not counted towards the
	# final score. Only the top 7 are. 
	selection += ['xxx', 'xyz', 'yyy']
	headers = {
		'origin': 'https://www.datcreativity.com',
		'referer': 'https://www.datcreativity.com/task'
	}
	data = {}
	for i, s in enumerate(selection):
		data[f'words-word{i+1}'] = s
	data['demographics-age'] = ''
	data['demographics-sex'] = 'none'
	data['demographics-country'] = 'none'
	r = requests.post('https://www.datcreativity.com/task', headers=headers, data=data)
	soup = BeautifulSoup(r.text, features='html.parser')
	# print(soup.prettify())
	score, percentile, table, errors = parse(soup)
	if score and percentile and table:
		val = (score, percentile, table)
	else: 
		print(str(len(errors)) + ' errors: ' + ','.join(selection))
		val = ('0.0', errors, len(errors))
	return val

def get_neighbor(res, selection):
	if flag_select_lowest_row:
		best_rows = sorted([(row[0], sum([int(val) for val in row[1:]])) for row in res[2]], key=lambda x:x[1])
		best_word = best_rows[0][0]
		element = selection.index(best_rows[0][0])
	else:
		element = random.randint(0, len(selection) - 1)
	new_word = random.choice(words)
	new_selection = [s for s in selection]
	new_selection[element] = new_word
	if mutate_two:
		if flag_select_lowest_row:
			best_word = best_rows[1][0]
			element = selection.index(best_rows[1][0])
		else:
			element = random.randint(0, len(selection) - 1)
		new_word = random.choice(words)
		new_selection[element] = new_word
	return new_selection

def get_acceptance_prob(old_val, new_val, temp):
	if new_val > old_val:
		return 1.0
	# import pdb; pdb.set_trace()
	if flag_pure_greedy:
		return 0
	return math.exp(-(old_val - new_val)/temp*5)

def print_row(val, selection):
	wordstext = ', '.join(selection)
	if val == '0.0':
		print(f'Error! {wordstext}')
	print(f'Score: {val[0]}\tPercentile: {val[1]}\t{wordstext}')

def write_row(val, selection):
	wordstext = ', '.join(selection)
	writer = f'{val[0]},{val[1]},{wordstext}\n'
	with open(OUTPUT, 'a') as f:
		f.write(writer)

# 100 iters, start 97.73 [mistrials, touch, intake, terminator, piece, washtubs, comfort] 
# 100.53,99.96,mistrials, tackles, injector, airport, photographs, washtubs, respiration
# 100 more
# 100.64,99.96,mistrials, ream, quiet, wholesales, courtesy, shield, project
# 100 more 
# 100.85,99.97,mistrials, truth, manager, wholesales, courtesy, washtubs, pushups
# 100 more, stable

# 100 iters, start random [truck, duplicates, outfits, flaps, march, limbs, bowl]
# 99.35,99.93,music, administrator, watt, offenses, splicer, reveille, canvases
# 100.23,99.96,stake, visit, gulfs, ohm, splicer, coughs, lessons
# 101.16,99.97,breast, visit, gulfs, ohm, splicer, downgrades, noun
# 101.44,99.98,breast, visit, gulfs, ohm, splicer, downgrades, rifles
# 101.53,99.98,breast, visit, gulfs, ohm, splicer, downgrades, mitt

# Score: 101.28	Percentile: 99.98	shipwright, refillable, scrambled, quartet, happening, uprightness, copyrights
# Score: 101.28	Percentile: 99.98	shipwright, refillable, scrambled, quartet, happening, uprightness, copyrights
# Score: 102.45	Percentile: 99.99	burgeons, photoelectric, comedies, talon, submitted, forum, impoverishing
# Score: 102.67	Percentile: 99.99	updated, debut, cols, epidermal, arbitration, pantheistic, yelled


# Optimization 1: only look at lowest row
# Score: 103.75	Percentile: 99.99	updated, debut, cols, ethnographers, episcopacy, soldering, yelled
# Score: 104.46	Percentile: 100.0	updated, debut, cols, prodigality, minister, soldering, relativists
# Score: 104.85	Percentile: 100.0	updated, debut, cols, petrify, minister, soldering, relativists
# Score: 105.11	Percentile: 100.0	updated, debut, cols, satrap, campus, soldering, relativists

# 400 runs, change lowest row:
# start: 66.25,3.93,income, profit, possible, estate, help, web, range, lead, kiss, rope
# end: Score: 102.05	Percentile: 99.98	con, douching, sacked, incorruptible, crunchiest, range, reopen
# Score: 103.0	Percentile: 99.99	con, douching, servility, inches, crunchiest, range, reopen

# https://twitter.com/thomasahle/status/1424178136716095492 109.5
# 109.5 views, reference, inch, niff, partnered, absconds, jujube



# 2000 greedy:
# Score: 103.89	Percentile: 99.99	initialising, beneficiaries, rebuffs, hardback, gear, lyrics, kiloton
# 3000 - Score: 104.67	Percentile: 100.0	initialising, beneficiaries, rebuffs, micron, gear, lyrics, finalist

selection = random.sample(words, 7)
if start_words:
	selection = start_words.split(', ')
res = get_results(selection)
print_row(res, selection)
while res[0] == '0.0':
	selection = random.sample(words, 7)
	res = get_results(selection)
max_res = (res, selection)
for i in range(0, k_max):
	print(f'Iteration {i}')
	# 0.999 to prevent division by 0
	temp = 1.0 - (i+0.999)/k_max
	new_selection = get_neighbor(res, selection)
	new_res = get_results(new_selection)
	while new_res[0] == '0.0':
		new_selection = get_neighbor(res, selection)
		new_res = get_results(new_selection)
	print_row(new_res, new_selection)
	# time.sleep(0.25)
	accept_prob = get_acceptance_prob(float(res[0]), float(new_res[0]), temp)
	print(f'Accept Prob: {accept_prob} Before: {float(res[0])} After:{float(new_res[0])}')
	rand = random.random()
	if i % 10 == 0:
		print('\n\n')
		print_row(max_res[0], max_res[1])
		print(max_res)
		print('\n\n')
	if float(new_res[0]) > float(max_res[0][0]):
		max_res = (new_res, new_selection)
	if accept_prob >= rand:
		selection = new_selection
		res = new_res
		print_row(new_res, new_selection)
		write_row(new_res, new_selection)

print('\n\n')
print_row(max_res[0], max_res[1])
print(max_res)


