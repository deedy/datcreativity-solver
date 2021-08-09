import requests
from bs4 import BeautifulSoup
import random
import re
import time
import math

words = []
# '/usr/share/dict/words' leads to invalid results 
FILE = '/usr/share/dict/words' # mostly errors in spelling
# FILE = 'data/nouns-91k.txt'
# FILE = 'data/nouns-6k.txt'
# FILE = 'data/nouns-sorted.txt' # too small
# FILE = 'data/nounlist-large.txt' #7k
FILE = 'data/corncob_lowercase.txt'
RESULTS = 'results.csv'
BATCH_SIZE = 10
ATTEMPTS = 1000
NUM_WORDS = 7
OUTPUT = 'anneal_105.csv'
flag_select_lowest_row = True
flag_select_custom_row = 3
mutate_two = False	
# Set this to '' to start from random
start_words = 'initialising, beneficiaries, rebuffs, micron, gear, lyrics, finalist'

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

def get_neighbor(res, selection, new_word):
	if flag_select_custom_row >= 0:
		element = flag_select_custom_row
	else:
		if flag_select_lowest_row:
			best_rows = sorted([(row[0], sum([int(val) for val in row[1:]])) for row in res[2]], key=lambda x:x[1])
			best_word = best_rows[0][0]
			element = selection.index(best_rows[0][0])
		else:
			element = random.randint(0, len(selection) - 1)
	new_selection = [s for s in selection]
	new_selection[element] = new_word
	if mutate_two and not flag_select_custom_row:
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
	return 0.0

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

# optimization over 200k^7 = 1.28*10^37, vs Chess 10^47
# Brute:
# Score: 105.49	Percentile: 100.0	alerts, debut, cols, satrap, campus, soldering, relativists
# Score: 106.41	Percentile: 100.0	alerts, debut, cols, satrap, acres, soldering, relativists


selection = random.sample(words, 7)
# Edit this or comment this out to start the optimization at this step
if start_words:
	selection = start_words.split(', ')
res = get_results(selection)
max_res = (res, selection)
print_row(res, selection)

# Comment out to look at words at random
# random.shuffle(words)
for i, w in enumerate(words):
	new_selection = get_neighbor(res, selection, w)
	new_res = get_results(new_selection)
	print_row(new_res, new_selection)
	if i % 10 == 0:
		print('\n\n')
		print_row(max_res[0], max_res[1])
		print(max_res)
		print('\n\n')
	if float(new_res[0]) > float(max_res[0][0]):
		max_res = (new_res, new_selection)
		print('New Max')
		print_row(new_res, new_selection)



print('\n\n')
print_row(max_res[0], max_res[1])
print(max_res)


