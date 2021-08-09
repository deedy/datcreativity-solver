import requests
from bs4 import BeautifulSoup
import random
import re
import time

# Best run achieved by O(1000s) of attempts at random from various word lists
# 97.73,99.84,mistrials, touch, intake, terminator, piece, washtubs, comfort, xxx, xyz, yyy

words = []
# '/usr/share/dict/words' leads to invalid results 
# FILE = '/usr/share/dict/words' # mostly errors in spelling
FILE = 'data/nouns-91k.txt'
FILE = 'data/nouns-6k.txt'
# FILE = 'data/nouns-sorted.txt' # too small
# FILE = 'data/nounlist-large.txt'
RESULTS = 'results.csv'
BATCH_SIZE = 10
ATTEMPTS = 1000
NUM_WORDS = 7
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

logs = []
for y in range(0, int(ATTEMPTS/BATCH_SIZE)):
	print(y)
	random.shuffle(words)
	for x in range(0, 10):
		selection = random.sample(words, 7)
		selection += ['xxx', 'xyz', 'yyy']
		print(selection)
		# selection = ['apple', 'orange', 'guava', 'strawberry', 'raspberry', 'mango', 'cherry', 'candy', 'fruit', 'banana']
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
			val = (errors, len(errors))
		logs.append((selection, val))
		time.sleep(1)

	writer = ''
	for wordsres, val in logs:
		wordstext = ', '.join(wordsres)
		if len(val) == 2:
			print(f'Error: {wordstext}')
			continue
		print(f'Score: {val[0]}\tPercentile: {val[1]}\t{wordstext}')
		writer += f'{val[0]},{val[1]},{wordstext}\n'
	with open(RESULTS, 'a') as f:
		f.write(writer)