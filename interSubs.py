#! /usr/bin/env python

# v. 2.7
# Interactive subtitles for `mpv` for language learners.

import os, subprocess, sys
import random, re, time
import requests
import threading, queue
import calendar, math, base64
import numpy
import ast

from bs4 import BeautifulSoup

from urllib.parse import quote
from json import loads

import warnings
from six.moves import urllib

from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QApplication, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QWidget
from PyQt5.QtGui import QPalette, QPaintEvent, QPainter, QPainterPath, QFont, QFontMetrics, QColor, QPen, QBrush

pth = os.path.expanduser('~/.config/mpv/scripts/')
os.chdir(pth)
import interSubs_config as config

pons_combos = ['enes', 'enfr', 'deen', 'enpl', 'ensl', 'defr', 'dees', 'deru', 'depl', 'desl', 'deit', 'dept', 'detr', 'deel', 'dela', 'espl', 'frpl', 'itpl', 'plru', 'essl', 'frsl', 'itsl', 'enit', 'enpt', 'enru', 'espt', 'esfr', 'delb', 'dezh', 'enzh', 'eszh', 'frzh', 'denl', 'arde', 'aren', 'dade', 'csde', 'dehu', 'deno', 'desv', 'dede', 'dedx']

# returns ([[word, translation]..], [morphology = '', gender = ''])
# pons.com
def pons(word):
	if config.lang_from + config.lang_to in pons_combos:
		url = 'http://en.pons.com/translate?q=%s&l=%s%s&in=%s' % (quote(word), config.lang_from, config.lang_to, config.lang_from)
	else:
		url = 'http://en.pons.com/translate?q=%s&l=%s%s&in=%s' % (quote(word), config.lang_to, config.lang_from, config.lang_from)

	pairs = []
	fname = 'urls/' + url.replace('/', "-")
	try:
		p = open(fname).read().split('=====/////-----')
		try:
			word_descr = p[1].strip()
		except:
			word_descr = ''

		if len(p[0].strip()):
			for pi in p[0].strip().split('\n\n'):
				pi = pi.split('\n')
				pairs.append([pi[0], pi[1]])
	except:
		p = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'}).text

		soup = BeautifulSoup(p, "lxml")
		trs = soup.find_all('dl')

		for tr in trs:
			try:
				tr1 = tr.find('dt').find('div', class_="source").get_text()
				tr1 = re.sub('\n|\r|\t', ' ', tr1)
				tr1 = re.sub(' +', ' ', tr1).strip()
				if not len(tr1):
					tr1 = '-'

				tr2 = tr.find('dd').find('div', class_="target").get_text()
				tr2 = re.sub('\n|\r|\t', ' ', tr2)
				tr2 = re.sub(' +', ' ', tr2).strip()
				if not len(tr2):
					tr2 = '-'
			except:
				continue

			pairs.append([tr1, tr2])

			if config.number_of_translations_to_save and len(pairs) > config.number_of_translations_to_save:
				break

		try:
			word_descr = soup.find_all('h2', class_='')
			if '<i class="icon-bolt">' not in str(word_descr[0]):
				word_descr = re.sub('\n|\r|\t', ' ', word_descr[0].get_text())
				word_descr = re.sub(' +', ' ', word_descr).replace('&lt;', '<').replace('&gt;', '>').replace(' · ', '·').replace(' , ', ', ').strip()
			else:
				word_descr = ''
		except:
			word_descr = ''

		# extra check against double-writing from rouge threads
		if not os.path.isfile(fname):
			print('\n\n'.join(e[0] + '\n' + e[1] for e in pairs), file=open(fname, 'a'))
			print('\n'+'=====/////-----'+'\n', file=open(fname, 'a'))
			print(word_descr, file=open(fname, 'a'))

	if len(word_descr):
		if word_descr.split(' ')[-1] == 'm':
			word_descr_gen = [word_descr[:-2], 'm']
		elif word_descr.split(' ')[-1] == 'f':
			word_descr_gen = [word_descr[:-2], 'f']
		elif word_descr.split(' ')[-1] == 'nt':
			word_descr_gen = [word_descr[:-3], 'nt']
		else:
			word_descr_gen = [word_descr, '']
	else:
		word_descr_gen = ['', '']

	return pairs, word_descr_gen

# https://github.com/ssut/py-googletrans
class TokenAcquirer(object):
	"""Google Translate API token generator
	translate.google.com uses a token to authorize the requests. If you are
	not Google, you do have this token and will have to pay for use.
	This class is the result of reverse engineering on the obfuscated and
	minified code used by Google to generate such token.
	The token is based on a seed which is updated once per hour and on the
	text that will be translated.
	Both are combined - by some strange math - in order to generate a final
	token (e.g. 744915.856682) which is used by the API to validate the
	request.
	This operation will cause an additional request to get an initial
	token from translate.google.com.
	Example usage:
		>>> from googletrans.gtoken import TokenAcquirer
		>>> acquirer = TokenAcquirer()
		>>> text = 'test'
		>>> tk = acquirer.do(text)
		>>> tk
		950629.577246
	"""

	RE_TKK = re.compile(r'tkk:\'(.+?)\'', re.DOTALL)
	RE_RAWTKK = re.compile(r'tkk:\'(.+?)\'', re.DOTALL)

	def __init__(self, tkk='0', session=None, host='translate.google.com'):
		self.session = session or requests.Session()
		self.tkk = tkk
		self.host = host if 'http' in host else 'https://' + host


	def rshift(self, val, n):
		"""python port for '>>>'(right shift with padding)
		"""
		return (val % 0x100000000) >> n
		
	def _update(self):
		"""update tkk
		"""
		# we don't need to update the base TKK value when it is still valid
		now = math.floor(int(time.time() * 1000) / 3600000.0)
		if self.tkk and int(self.tkk.split('.')[0]) == now:
			return

		r = self.session.get(self.host)

		raw_tkk = self.RE_TKK.search(r.text)
		if raw_tkk:
			self.tkk = raw_tkk.group(1)
			return

		# this will be the same as python code after stripping out a reserved word 'var'
		code = unicode(self.RE_TKK.search(r.text).group(1)).replace('var ', '')
		# unescape special ascii characters such like a \x3d(=)
		if PY3:  # pragma: no cover
			code = code.encode().decode('unicode-escape')
		else:  # pragma: no cover
			code = code.decode('string_escape')

		if code:
			tree = ast.parse(code)
			visit_return = False
			operator = '+'
			n, keys = 0, dict(a=0, b=0)
			for node in ast.walk(tree):
				if isinstance(node, ast.Assign):
					name = node.targets[0].id
					if name in keys:
						if isinstance(node.value, ast.Num):
							keys[name] = node.value.n
						# the value can sometimes be negative
						elif isinstance(node.value, ast.UnaryOp) and \
								isinstance(node.value.op, ast.USub):  # pragma: nocover
							keys[name] = -node.value.operand.n
				elif isinstance(node, ast.Return):
					# parameters should be set after this point
					visit_return = True
				elif visit_return and isinstance(node, ast.Num):
					n = node.n
				elif visit_return and n > 0:
					# the default operator is '+' but implement some more for
					# all possible scenarios
					if isinstance(node, ast.Add):  # pragma: nocover
						pass
					elif isinstance(node, ast.Sub):  # pragma: nocover
						operator = '-'
					elif isinstance(node, ast.Mult):  # pragma: nocover
						operator = '*'
					elif isinstance(node, ast.Pow):  # pragma: nocover
						operator = '**'
					elif isinstance(node, ast.BitXor):  # pragma: nocover
						operator = '^'
			# a safety way to avoid Exceptions
			clause = compile('{1}{0}{2}'.format(
				operator, keys['a'], keys['b']), '', 'eval')
			value = eval(clause, dict(__builtin__={}))
			result = '{}.{}'.format(n, value)

			self.tkk = result

	def _lazy(self, value):
		"""like lazy evalution, this method returns a lambda function that
		returns value given.
		We won't be needing this because this seems to have been built for
		code obfuscation.
		the original code of this method is as follows:
		   ... code-block: javascript
			   var ek = function(a) {
				return function() {
					return a;
				};
			   }
		"""
		return lambda: value

	def _xr(self, a, b):
		size_b = len(b)
		c = 0
		while c < size_b - 2:
			d = b[c + 2]
			d = ord(d[0]) - 87 if 'a' <= d else int(d)
			d = self.rshift(a, d) if '+' == b[c + 1] else a << d
			a = a + d & 4294967295 if '+' == b[c] else a ^ d

			c += 3
		return a

	def acquire(self, text):
		a = []
		# Convert text to ints
		for i in text:
			val = ord(i)
			if val < 0x10000:
				a += [val]
			else:
				# Python doesn't natively use Unicode surrogates, so account for those
				a += [
					math.floor((val - 0x10000)/0x400 + 0xD800),
					math.floor((val - 0x10000)%0x400 + 0xDC00)
					]

		b = self.tkk if self.tkk != '0' else ''
		d = b.split('.')
		b = int(d[0]) if len(d) > 1 else 0

		# assume e means char code array
		e = []
		g = 0
		size = len(text)
		while g < size:
			l = a[g]
			# just append if l is less than 128(ascii: DEL)
			if l < 128:
				e.append(l)
			# append calculated value if l is less than 2048
			else:
				if l < 2048:
					e.append(l >> 6 | 192)
				else:
					# append calculated value if l matches special condition
					if (l & 64512) == 55296 and g + 1 < size and \
							a[g + 1] & 64512 == 56320:
						g += 1
						l = 65536 + ((l & 1023) << 10) + (a[g] & 1023) # This bracket is important
						e.append(l >> 18 | 240)
						e.append(l >> 12 & 63 | 128)
					else:
						e.append(l >> 12 | 224)
					e.append(l >> 6 & 63 | 128)
				e.append(l & 63 | 128)   
			g += 1
		a = b
		for i, value in enumerate(e):
			a += value
			a = self._xr(a, '+-a^+6')
		a = self._xr(a, '+-3^+b+-f')
		a ^= int(d[1]) if len(d) > 1 else 0
		if a < 0:  # pragma: nocover
			a = (a & 2147483647) + 2147483648
		a %= 1000000  # int(1E6)

		return '{}.{}'.format(a, a ^ b)

	def do(self, text):
		self._update()
		tk = self.acquire(text)
		return tk

# translate.google.com
def google(word):
	url = 'https://translate.google.com/translate_a/single?client=t&sl={lang_from}&tl={lang_to}&hl={lang_to}&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&otf=1&pc=1&ssel=3&tsel=3&kc=2&q={word}'.format(lang_from = config.lang_from, lang_to = config.lang_to, word = quote(word))

	pairs = []
	fname = 'urls/' + url.replace('/', "-")
	try:
		p = open(fname).read().split('=====/////-----')
		try:
			word_descr = p[1].strip()
		except:
			word_descr = ''

		for pi in p[0].strip().split('\n\n'):
			pi = pi.split('\n')
			pairs.append([pi[0], pi[1]])
	except:
		acquirer = TokenAcquirer()
		tk = acquirer.do(word)

		url = '{url}&tk={tk}'.format(url = url, tk = tk)
		p = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'}).text
		p = loads(p)

		try:
			pairs.append([p[0][0][0], p[0][0][1]])
		except:
			pass

		if p[1] != None:
			for translations in p[1]:
				for translation in translations[2]:
					try:
						t1 = translation[5] + ' ' + translation[0]
					except:
						t1 = translation[0]

					t2 = ', '.join(translation[1])

					if not len(t1):
						t1 = '-'
					if not len(t2):
						t2 = '-'

					pairs.append([t1, t2])

		word_descr = ''
		# extra check against double-writing from rouge threads
		if not os.path.isfile(fname):
			print('\n\n'.join(e[0] + '\n' + e[1] for e in pairs), file=open(fname, 'a'))
			print('\n'+'=====/////-----'+'\n', file=open(fname, 'a'))
			print(word_descr, file=open(fname, 'a'))

	return pairs, ['', '']

# reverso.net
def reverso(word):
	reverso_combos = {'ar':'Arabic', 'de':'German', 'en':'English', 'es':'Spanish', 'fr':'French', 'he':'Hebrew', 'it':'Italian', 'nl':'Dutch', 'pl':'Polish', 'pt':'Portuguese', 'ro':'Romanian', 'ru':'Russian'}

	if not config.lang_from in reverso_combos and not config.lang_to in reverso_combos:
		return [['Language code is not correct.', '']], ['', '']

	url = 'http://context.reverso.net/translation/%s-%s/%s' % (reverso_combos[config.lang_from].lower(), reverso_combos[config.lang_to].lower(), quote(word))

	pairs = []
	fname = 'urls/' + url.replace('/', "-")
	try:
		p = open(fname).read().split('=====/////-----')

		if len(p[0].strip()):
			for pi in p[0].strip().split('\n\n'):
				pi = pi.split('\n')
				pairs.append([pi[0], pi[1]])
	except:
		p = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'}).text

		soup = BeautifulSoup(p, "lxml")
		trs = soup.find_all(class_ = re.compile('translation.*ltr.*'))
		exmpls = soup.find_all(class_ = 'example')

		tr_combined = []
		for tr in trs:
			tr_combined.append(tr.get_text().strip().replace('\n', ' '))

			if len(tr_combined) == 4:
				pairs.append(['-', ' :: '.join(tr_combined)])
				tr_combined = []

		for exmpl in exmpls:
			pairs.append([x.strip() for x in exmpl.get_text().split('\n') if len(x.strip())])

		# extra check against double-writing from rouge threads
		if not os.path.isfile(fname):
			print('\n\n'.join(e[0] + '\n' + e[1] for e in pairs), file=open(fname, 'a'))
			print('\n'+'=====/////-----'+'\n', file=open(fname, 'a'))

	return pairs, ['', '']

# linguee.com (unfinished; site blocks frequent requests)
def linguee(word):
	url = 'https://www.linguee.com/german-english/search?source=german&query=%s' % quote(word)

	pairs = []
	fname = 'urls/' + url.replace('/', "-")
	try:
		p = open(fname).read().split('=====/////-----')
		try:
			word_descr = p[1].strip()
		except:
			word_descr = ''

		for pi in p[0].strip().split('\n\n'):
			pi = pi.split('\n')
			pairs.append([pi[0], pi[1]])
	except:
		#p = open('/home/lom/d/1.html', encoding="ISO-8859-15").read()
		p = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'}).text

		soup = BeautifulSoup(p, "lxml")
		trs = soup.find_all('div', class_="lemma featured")

		for tr in trs:
			pairs.append([tr.find_all('a')[0].get_text(), '-'])
			for tr2 in tr.find_all('a')[1:]:
				if len(tr2.get_text()):
					#print(tr2.get_text())
					pairs.append(['-', tr2.get_text()])
		word_descr = ''

		# extra check against double-writing from rouge threads
		if not os.path.isfile(fname):
			print('\n\n'.join(e[0] + '\n' + e[1] for e in pairs), file=open(fname, 'a'))
			print('\n'+'=====/////-----'+'\n', file=open(fname, 'a'))
			print(word_descr, file=open(fname, 'a'))

	return pairs, ['', '']

# dict.cc
def dict_cc(word):
	url = 'https://%s-%s.dict.cc/?s=%s' % (config.lang_from, config.lang_to, quote(word))

	pairs = []
	fname = 'urls/' + url.replace('/', "-")
	try:
		p = open(fname).read().split('=====/////-----')
		try:
			word_descr = p[1].strip()
		except:
			word_descr = ''

		if len(p[0].strip()):
			for pi in p[0].strip().split('\n\n'):
				pi = pi.split('\n')
				pairs.append([pi[0], pi[1]])
	except:
		p = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'}).text

		p = re.sub('<div style="float:right;color:#999">\d*</div>', '', p)
		p = re.sub('<span style="color:#666;font-size:10px;padding:0 2px;position:relative;top:-3px">\d*</span>', '', p)

		soup = BeautifulSoup(p, "lxml")
		trs = soup.find_all('tr', id = re.compile('tr\d*'))

		for tr in trs:
			tr2 = tr.find_all('td', class_ = 'td7nl')
			pairs.append([tr2[1].get_text(), tr2[0].get_text()])

			if config.number_of_translations_to_save and len(pairs) > config.number_of_translations_to_save:
				break

		word_descr = ''

		# extra check against double-writing from rouge threads
		if not os.path.isfile(fname):
			print('\n\n'.join(e[0] + '\n' + e[1] for e in pairs), file=open(fname, 'a'))
			print('\n'+'=====/////-----'+'\n', file=open(fname, 'a'))
			print(word_descr, file=open(fname, 'a'))

	return pairs, ['', '']

# redensarten-index.de
def redensarten(word):
	if len(word) < 3:
		return [], ['', '']

	url = 'https://www.redensarten-index.de/suche.php?suchbegriff=' + quote(word) + '&bool=relevanz&gawoe=an&suchspalte%5B%5D=rart_ou&suchspalte%5B%5D=rart_varianten_ou&suchspalte%5B%5D=erl_ou&suchspalte%5B%5D=erg_ou'

	pairs = []
	fname = 'urls/' + url.replace('/', "-")
	try:
		p = open(fname).read().split('=====/////-----')
		try:
			word_descr = p[1].strip()
		except:
			word_descr = ''

		if len(p[0].strip()):
			for pi in p[0].strip().split('\n\n'):
				pi = pi.split('\n')
				pairs.append([pi[0], pi[1]])
	except:
		p = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'})
		p.encoding = 'utf-8'
		p = p.text

		soup = BeautifulSoup(p, "lxml")

		for a in soup.find_all('a', class_ = 'autosyn-icon'):
			a.decompose()

		try:
			table = soup.find_all('table', id = 'tabelle')[0]
			trs = table.find_all('tr')

			for tr in trs[1:]:
				tds = tr.find_all('td')
				if len(tds) > 1:
					pairs.append([ re.sub(' +', ' ', tds[0].get_text()).strip(), re.sub(' +', ' ', tds[1].get_text()).strip() ])
		except:
			pass

		word_descr = ''

		# extra check against double-writing from rouge threads
		if not os.path.isfile(fname):
			print('\n\n'.join(e[0] + '\n' + e[1] for e in pairs), file=open(fname, 'a'))
			print('\n'+'=====/////-----'+'\n', file=open(fname, 'a'))
			print(word_descr, file=open(fname, 'a'))

	return pairs, ['', '']

# leo.org
def leo(word):
	language = config.lang_from if config.lang_from != 'de' else config.lang_to

	url = "https://dict.leo.org/dictQuery/m-vocab/%sde/query.xml?tolerMode=nof&rmWords=off&rmSearch=on&searchLoc=0&resultOrder=basic&multiwordShowSingle=on&lang=de&search=%s" % (language, word)

	pairs = []
	fname = 'urls/' + url.replace('/', "-")
	try:
		p = open(fname).read().split('=====/////-----')
		try:
			word_descr = p[1].strip()
		except:
			word_descr = ''

		if len(p[0].strip()):
			for pi in p[0].strip().split('\n\n'):
				pi = pi.split('\n')
				pairs.append([pi[0], pi[1]])
	except:
		req = requests.get(url.format(lang=language))

		content = BeautifulSoup(req.text, "xml")
		pairs = []
		for section in content.sectionlist.findAll('section'):
			if int(section['sctCount']):
				for entry in section.findAll('entry'):
					res0 = entry.find('side', attrs = {'hc' : '0'})
					res1 = entry.find('side', attrs = {'hc' : '1'})
					if res0 and res1:
						line0 = re.sub('\s+', ' ', res0.repr.getText())
						line1 = re.sub('\s+', ' ', res1.repr.getText())
						line0 = line0.rstrip('|').strip()
						line1 = line1.rstrip('|').strip()

						if res0.attrs['lang'] == config.lang_from:
							pairs.append([line0, line1])
						else:
							pairs.append([line1, line0])

		word_descr = ''
		# extra check against double-writing from rouge threads
		if not os.path.isfile(fname):
			print('\n\n'.join(e[0] + '\n' + e[1] for e in pairs), file=open(fname, 'a'))
			print('\n'+'=====/////-----'+'\n', file=open(fname, 'a'))
			print(word_descr, file=open(fname, 'a'))

	return pairs, ['', '']

# offline dictionary with word \t translation
def tab_divided_dict(word):
	if word in offdict:
		tr = re.sub('<.*?>', '', offdict[word]) if config.tab_divided_dict_remove_tags_B else offdict[word]
		tr = tr.replace('\\n', '\n').replace('\\~', '~')
		return [[tr, '-']], ['', '']
	else:
		return [], ['', '']

# morfix.co.il
def morfix(word):

	url = "http://www.morfix.co.il/en/%s" % quote(word)

	pairs = []
	fname = 'urls/' + url.replace('/', "-")
	try:
		p = open(fname).read().split('=====/////-----')
		try:
			word_descr = p[1].strip()
		except:
			word_descr = ''

		if len(p[0].strip()):
			for pi in p[0].strip().split('\n\n'):
				pi = pi.split('\n')
				pairs.append([pi[0], pi[1]])
	except:
		req = requests.get(url)
		soup = BeautifulSoup(req.text, "lxml")
		divs = soup.find_all('div', class_ = 'title_ph')

		pairs = []
		for div in divs:
			he = div.find('div', class_ = re.compile('translation_he'))
			he = re.sub('\s+', ' ', he.get_text()).strip()

			en = div.find('div', class_ = re.compile('translation_en'))
			en = re.sub('\s+', ' ', en.get_text()).strip()

			if config.lang_from == 'he':
				pairs.append([he, en])
			else:
				pairs.append([en, he])

		word_descr = ''
		# extra check against double-writing from rouge threads
		if not os.path.isfile(fname):
			print('\n\n'.join(e[0] + '\n' + e[1] for e in pairs), file=open(fname, 'a'))
			print('\n'+'=====/////-----'+'\n', file=open(fname, 'a'))
			print(word_descr, file=open(fname, 'a'))

	return pairs, ['', '']

# deepl.com
# https://github.com/EmilioK97/pydeepl
def deepl(text):
	l1 = config.lang_from.upper()
	l2 = config.lang_to.upper()

	if len(text) > 5000:
		return 'Text too long (limited to 5000 characters).'

	parameters = {
		'jsonrpc': '2.0',
		'method': 'LMT_handle_jobs',
		'params': {
			'jobs': [
				{
					'kind':'default',
					'raw_en_sentence': text
				}
			],
			'lang': {

				'source_lang_user_selected': l1,
				'target_lang': l2
			}
		}
	}

	response = requests.post('https://www2.deepl.com/jsonrpc', json=parameters).json()
	print(response)
	if 'result' not in response:
		return 'DeepL call resulted in a unknown result.'

	translations = response['result']['translations']

	if len(translations) == 0 \
			or translations[0]['beams'] is None \
			or translations[0]['beams'][0]['postprocessed_sentence'] is None:
		return 'No translations found.'

	return translations[0]['beams'][0]['postprocessed_sentence']

def listen(word, type = 'gtts'):
	if type == 'pons':
		if config.lang_from + config.lang_to in pons_combos:
			url = 'http://en.pons.com/translate?q=%s&l=%s%s&in=%s' % (quote(word), config.lang_from, config.lang_to, config.lang_from)
		else:
			url = 'http://en.pons.com/translate?q=%s&l=%s%s&in=%s' % (quote(word), config.lang_to, config.lang_from, config.lang_from)

		p = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'}).text
		x = re.findall('<dl id="([a-zA-Z0-9]*?)" class="dl-horizontal kne(.*?)</dl>', p, re.DOTALL)
		x2 = re.findall('class="audio tts trackable trk-audio" data-pons-lang="(.*?)"', x[0][1])

		for l in x2:
			if config.lang_from in l:
				mp3 = 'http://sounds.pons.com/audio_tts/%s/%s' % (l, x[0][0])
				break

		os.system('(cd /tmp; wget ' + mp3 + '; mpv --load-scripts=no --loop=1 --volume=40 --force-window=no ' + mp3.split('/')[-1] + '; rm ' + mp3.split('/')[-1] + ') &')
	elif type == 'gtts':
		gTTS(text = word, lang = config.lang_from, slow = False).save('/tmp/gtts_word.mp3')
		os.system('(mpv --load-scripts=no --loop=1 --volume=75 --force-window=no ' + '/tmp/gtts_word.mp3' + '; rm ' + '/tmp/gtts_word.mp3' + ') &')
	elif type == 'forvo':
		url = 'https://forvo.com/word/%s/%s/' % (config.lang_from, quote(word))

		try:
			data = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'}).text

			soup = BeautifulSoup(data, "lxml")
			trs = soup.find_all('article', class_ = 'pronunciations')[0].find_all('span', class_ = 'play')

			mp3s = ''
			for tr in trs[:2]:
				tr = tr['onclick']
				tr = re.findall('Play\((.*?)\)', tr)[0]
				tr = tr.split(',')[4].replace("'", '')
				tr = base64.b64decode(tr)
				tr = tr.decode("utf-8")

				mp3s += 'mpv --load-scripts=no --loop=1 --volume=111 --force-window=no https://audio00.forvo.com/audios/mp3/%s ; ' % tr
			os.system('(%s) &' % mp3s)
		except:
			return

# https://github.com/Boudewijn26/gTTS-token
class Token:
	""" Token (Google Translate Token)
	Generate the current token key and allows generation of tokens (tk) with it
	Python version of `token-script.js` itself from translate.google.com
	"""

	SALT_1 = "+-a^+6"
	SALT_2 = "+-3^+b+-f"

	def __init__(self):
		self.token_key = None

	def calculate_token(self, text, seed=None):
		""" Calculate the request token (`tk`) of a string
		:param text: str The text to calculate a token for
		:param seed: str The seed to use. By default this is the number of hours since epoch
		"""

		if seed is None:
			seed = self._get_token_key()

		[first_seed, second_seed] = seed.split(".")

		try:
			d = bytearray(text.encode('UTF-8'))
		except UnicodeDecodeError:
			# This will probably only occur when d is actually a str containing UTF-8 chars, which means we don't need
			# to encode.
			d = bytearray(text)

		a = int(first_seed)
		for value in d:
			a += value
			a = self._work_token(a, self.SALT_1)
		a = self._work_token(a, self.SALT_2)
		a ^= int(second_seed)
		if 0 > a:
			a = (a & 2147483647) + 2147483648
		a %= 1E6
		a = int(a)
		return str(a) + "." + str(a ^ int(first_seed))

	def _get_token_key(self):
		if self.token_key is not None:
			return self.token_key

		response = requests.get("https://translate.google.com/")
		tkk_expr = re.search("(tkk:.*?),", response.text)
		if not tkk_expr:
			raise ValueError(
				"Unable to find token seed! Did https://translate.google.com change?"
			)

		tkk_expr = tkk_expr.group(1)
		try:
			# Grab the token directly if already generated by function call
			result = re.search("\d{6}\.[0-9]+", tkk_expr).group(0)
		except AttributeError:
			# Generate the token using algorithm
			timestamp = calendar.timegm(time.gmtime())
			hours = int(math.floor(timestamp / 3600))
			a = re.search("a\\\\x3d(-?\d+);", tkk_expr).group(1)
			b = re.search("b\\\\x3d(-?\d+);", tkk_expr).group(1)

			result = str(hours) + "." + str(int(a) + int(b))

		self.token_key = result
		return result

	""" Functions used by the token calculation algorithm """
	def _rshift(self, val, n):
		return val >> n if val >= 0 else (val + 0x100000000) >> n

	def _work_token(self, a, seed):
		for i in range(0, len(seed) - 2, 3):
			char = seed[i + 2]
			d = ord(char[0]) - 87 if char >= "a" else int(char)
			d = self._rshift(a, d) if seed[i + 1] == "+" else a << d
			a = a + d & 4294967295 if seed[i] == "+" else a ^ d
		return a

# https://github.com/pndurette/gTTS
class gTTS:
	""" gTTS (Google Text to Speech): an interface to Google's Text to Speech API """

	# Google TTS API supports two read speeds
	# (speed <= 0.3: slow; speed > 0.3: normal; default: 1)
	class Speed:
		SLOW = 0.3
		NORMAL = 1

	GOOGLE_TTS_URL = 'https://translate.google.com/translate_tts'
	MAX_CHARS = 100 # Max characters the Google TTS API takes at a time
	LANGUAGES = {
		'af' : 'Afrikaans',
		'sq' : 'Albanian',
		'ar' : 'Arabic',
		'hy' : 'Armenian',
		'bn' : 'Bengali',
		'ca' : 'Catalan',
		'zh' : 'Chinese',
		'zh-cn' : 'Chinese (Mandarin/China)',
		'zh-tw' : 'Chinese (Mandarin/Taiwan)',
		'zh-yue' : 'Chinese (Cantonese)',
		'hr' : 'Croatian',
		'cs' : 'Czech',
		'da' : 'Danish',
		'nl' : 'Dutch',
		'en' : 'English',
		'en-au' : 'English (Australia)',
		'en-uk' : 'English (United Kingdom)',
		'en-us' : 'English (United States)',
		'eo' : 'Esperanto',
		'fi' : 'Finnish',
		'fr' : 'French',
		'de' : 'German',
		'el' : 'Greek',
		'hi' : 'Hindi',
		'hu' : 'Hungarian',
		'is' : 'Icelandic',
		'id' : 'Indonesian',
		'it' : 'Italian',
		'iw' : 'Hebrew',
		'ja' : 'Japanese',
		'km' : 'Khmer (Cambodian)',
		'ko' : 'Korean',
		'la' : 'Latin',
		'lv' : 'Latvian',
		'mk' : 'Macedonian',
		'no' : 'Norwegian',
		'pl' : 'Polish',
		'pt' : 'Portuguese',
		'ro' : 'Romanian',
		'ru' : 'Russian',
		'sr' : 'Serbian',
		'si' : 'Sinhala',
		'sk' : 'Slovak',
		'es' : 'Spanish',
		'es-es' : 'Spanish (Spain)',
		'es-us' : 'Spanish (United States)',
		'sw' : 'Swahili',
		'sv' : 'Swedish',
		'ta' : 'Tamil',
		'th' : 'Thai',
		'tr' : 'Turkish',
		'uk' : 'Ukrainian',
		'vi' : 'Vietnamese',
		'cy' : 'Welsh'
	}

	def __init__(self, text, lang = 'en', slow = False, debug = False):
		self.debug = debug
		if lang.lower() not in self.LANGUAGES:
			raise Exception('Language not supported: %s' % lang)
		else:
			self.lang = lang.lower()

		if not text:
			raise Exception('No text to speak')
		else:
			self.text = text

		# Read speed
		if slow:
			self.speed = self.Speed().SLOW
		else:
			self.speed = self.Speed().NORMAL


		# Split text in parts
		if self._len(text) <= self.MAX_CHARS:
			text_parts = [text]
		else:
			text_parts = self._tokenize(text, self.MAX_CHARS)

		# Clean
		def strip(x): return x.replace('\n', '').strip()
		text_parts = [strip(x) for x in text_parts]
		text_parts = [x for x in text_parts if len(x) > 0]
		self.text_parts = text_parts

		# Google Translate token
		self.token = Token()

	def save(self, savefile):
		""" Do the Web request and save to `savefile` """
		with open(savefile, 'wb') as f:
			self.write_to_fp(f)

	def write_to_fp(self, fp):
		""" Do the Web request and save to a file-like object """
		for idx, part in enumerate(self.text_parts):
			payload = { 'ie' : 'UTF-8',
						'q' : part,
						'tl' : self.lang,
						'ttsspeed' : self.speed,
						'total' : len(self.text_parts),
						'idx' : idx,
						'client' : 'tw-ob',
						'textlen' : self._len(part),
						'tk' : self.token.calculate_token(part)}
			headers = {
				"Referer" : "http://translate.google.com/",
				"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36"
			}
			if self.debug: print(payload)
			try:
				# Disable requests' ssl verify to accomodate certain proxies and firewalls
				# Filter out urllib3's insecure warnings. We can live without ssl verify here
				with warnings.catch_warnings():
					warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
					r = requests.get(self.GOOGLE_TTS_URL,
									 params=payload,
									 headers=headers,
									 proxies=urllib.request.getproxies(),
									 verify=False)
				if self.debug:
					print("Headers: {}".format(r.request.headers))
					print("Request url: {}".format(r.request.url))
					print("Response: {}, Redirects: {}".format(r.status_code, r.history))
				r.raise_for_status()
				for chunk in r.iter_content(chunk_size=1024):
					fp.write(chunk)
			except Exception as e:
				raise

	def _len(self, text):
		""" Get char len of `text`, after decoding if Python 2 """
		try:
			# Python 2
			return len(text.decode('utf8'))
		except AttributeError:
			# Python 3
			return len(text)

	def _tokenize(self, text, max_size):
		""" Tokenizer on basic roman punctuation """

		punc = "¡!()[]¿?.,;:—«»\n"
		punc_list = [re.escape(c) for c in punc]
		pattern = '|'.join(punc_list)
		parts = re.split(pattern, text)

		min_parts = []
		for p in parts:
			min_parts += self._minimize(p, " ", max_size)
		return min_parts

	def _minimize(self, thestring, delim, max_size):
		""" Recursive function that splits `thestring` in chunks
		of maximum `max_size` chars delimited by `delim`. Returns list. """

		if self._len(thestring) > max_size:
			idx = thestring.rfind(delim, 0, max_size)
			return [thestring[:idx]] + self._minimize(thestring[idx:], delim, max_size)
		else:
			return [thestring]

def mpv_pause():
	os.system('echo \'{ "command": ["set_property", "pause", true] }\' | socat - "' + mpv_socket + '" > /dev/null')

def mpv_resume():
	os.system('echo \'{ "command": ["set_property", "pause", false] }\' | socat - "' + mpv_socket + '" > /dev/null')

def mpv_pause_status():
	stdoutdata = subprocess.getoutput('echo \'{ "command": ["get_property", "pause"] }\' | socat - "' + mpv_socket + '"')

	try:
		return loads(stdoutdata)['data']
	except:
		return mpv_pause_status()

def mpv_fullscreen_status():
	stdoutdata = subprocess.getoutput('echo \'{ "command": ["get_property", "fullscreen"] }\' | socat - "' + mpv_socket + '"')

	try:
		return loads(stdoutdata)['data']
	except:
		return mpv_fullscreen_status()

def mpv_message(message, timeout = 3000):
	os.system('echo \'{ "command": ["show-text", "' + message + '", "' + str(timeout) + '"] }\' | socat - "' + mpv_socket + '" > /dev/null')

def stripsd2(phrase):
	return ''.join(e for e in phrase.strip().lower() if e == ' ' or (e.isalnum() and not e.isdigit())).strip()

def r2l(l):
	l2 = ''

	try:
		l2 = re.findall('(?!%)\W+$', l)[0][::-1]
	except:
		pass

	l2 += re.sub('^\W+|(?!%)\W+$', '', l)

	try:
		l2 += re.findall('^\W+', l)[0][::-1]
	except:
		pass

	return l2

def split_long_lines(line, chunks = 2, max_symbols_per_line = False):
	if max_symbols_per_line:
		chunks = 0
		while 1:
			chunks += 1
			new_lines = []
			for i in range(chunks):
				new_line = ' '.join(numpy.array_split(line.split(' '), chunks)[i])
				new_lines.append(new_line)

			if len(max(new_lines, key = len)) <= max_symbols_per_line:
				return '\n'.join(new_lines)
	else:
		new_lines = []
		for i in range(chunks):
			new_line = ' '.join(numpy.array_split(line.split(' '), chunks)[i])
			new_lines.append(new_line)

		return '\n'.join(new_lines)

def dir2(name):
	print('\n'.join(dir( name )))
	exit()

class thread_subtitles(QObject):
	update_subtitles = pyqtSignal(bool, bool)

	@pyqtSlot()
	def main(self):
		global subs

		was_hidden = 0
		inc = 0
		auto_pause_2_ind = 0
		last_updated = time.time()

		while 1:
			time.sleep(config.update_time)

			# hide subs when mpv isn't in focus or in fullscreen
			if inc * config.update_time > config.focus_checking_time - 0.0001:
				while 'mpv' not in subprocess.getoutput('xdotool getwindowfocus getwindowname') or (config.hide_when_not_fullscreen_B and not mpv_fullscreen_status()) or (os.path.exists(mpv_socket + '_hide')):
					if not was_hidden:
						self.update_subtitles.emit(True, False)
						was_hidden = 1
					else:
						time.sleep(config.focus_checking_time)
				inc = 0
			inc += 1

			if was_hidden:
				was_hidden = 0
				self.update_subtitles.emit(False, False)
				continue

			try:
				tmp_file_subs = open(sub_file).read()
			except:
				continue

			if config.extend_subs_duration2max_B and not len(tmp_file_subs):
				if not config.extend_subs_duration_limit_sec:
					continue
				if config.extend_subs_duration_limit_sec > time.time() - last_updated:
					continue

			last_updated = time.time()

			# automatically switch into Hebrew if it's detected
			if config.lang_from != 'he' and config.lang_from != 'iw' and any((c in set('קראטוןםפשדגכעיחלךףזסבהנמצתץ')) for c in tmp_file_subs):
				config.lang_from = 'he'

				frf = random.choice(config.he_fonts)
				config.style_subs = re.sub('font-family: ".*?";', lambda ff: 'font-family: "%s";' % frf, config.style_subs, flags = re.I)

				config.R2L_from_B = True
				config.translation_function_names = config.translation_function_names_2
				config.listen_via = 'forvo'

				os.system('notify-send -i none -t 1111 "He"')
				os.system('notify-send -i none -t 1111 "%s"' % str(frf))

				self.update_subtitles.emit(False, True)

			while tmp_file_subs != subs:
				if config.auto_pause == 2:
					if not auto_pause_2_ind and len(re.sub(' +', ' ', stripsd2(subs.replace('\n', ' '))).split(' ')) > config.auto_pause_min_words - 1 and not mpv_pause_status():
						mpv_pause()
						auto_pause_2_ind = 1

					if auto_pause_2_ind and mpv_pause_status():
						break

					auto_pause_2_ind = 0

				subs = tmp_file_subs

				if config.auto_pause == 1:
					if len(re.sub(' +', ' ', stripsd2(subs.replace('\n', ' '))).split(' ')) > config.auto_pause_min_words - 1:
						mpv_pause()

				self.update_subtitles.emit(False, False)

				break

class thread_translations(QObject):
	get_translations = pyqtSignal(str, int, bool)

	@pyqtSlot()
	def main(self):
		while 1:
			to_new_word = False

			try:
				word, globalX = config.queue_to_translate.get(False)
			except:
				time.sleep(config.update_time)
				continue

			# changing cursor to hourglass during translation
			QApplication.setOverrideCursor(Qt.WaitCursor)

			threads = []
			for translation_function_name in config.translation_function_names:
				threads.append(threading.Thread(target = globals()[translation_function_name], args = (word,)))
			for x in threads:
				x.start()
			while any(thread.is_alive() for thread in threads):
				if config.queue_to_translate.qsize():
					to_new_word = True
					break
				time.sleep(config.update_time)

			QApplication.restoreOverrideCursor()

			if to_new_word:
				continue

			if config.block_popup:
				continue

			self.get_translations.emit(word, globalX, False)

# drawing layer
# because can't calculate outline with precision
class drawing_layer(QLabel):
	def __init__(self, line, subs, parent=None):
		super().__init__(None)
		self.line = line
		self.setStyleSheet(config.style_subs)
		self.psuedo_line = 0

	def draw_text_n_outline(self, painter: QPainter, x, y, outline_width, outline_blur, text):
		outline_color = QColor(config.outline_color)

		font = self.font()
		text_path = QPainterPath()
		if config.R2L_from_B:
			text_path.addText(x, y, font, ' ' + r2l(text.strip()) + ' ')
		else:
			text_path.addText(x, y, font, text)

		# draw blur
		range_width = range(outline_width, outline_width + outline_blur)
		# ~range_width = range(outline_width + outline_blur, outline_width, -1)

		for width in range_width:
			if width == min(range_width):
				alpha = 200
			else:
				alpha = (max(range_width) - width) / max(range_width) * 200

			blur_color = QColor(outline_color.red(), outline_color.green(), outline_color.blue(), alpha)
			blur_brush = QBrush(blur_color, Qt.SolidPattern)
			blur_pen = QPen(blur_brush, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

			painter.setPen(blur_pen)
			painter.drawPath(text_path)

		# draw outline
		outline_color = QColor(outline_color.red(), outline_color.green(), outline_color.blue(), 255)
		outline_brush = QBrush(outline_color, Qt.SolidPattern)
		outline_pen = QPen(outline_brush, outline_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

		painter.setPen(outline_pen)
		painter.drawPath(text_path)

		# draw text
		color = self.palette().color(QPalette.Text)
		painter.setPen(color)
		painter.drawText(x, y, text)

	if config.outline_B:
		def paintEvent(self, evt: QPaintEvent):
			if not self.psuedo_line:
				self.psuedo_line = 1
				return

			x = y = 0
			y += self.fontMetrics().ascent()
			painter = QPainter(self)

			self.draw_text_n_outline(
				painter,
				x,
				y + config.outline_top_padding - config.outline_bottom_padding,
				config.outline_thickness,
				config.outline_blur,
				text = self.line
				)

		def resizeEvent(self, *args):
			self.setFixedSize(
				self.fontMetrics().width(self.line),
				self.fontMetrics().height() +
					config.outline_bottom_padding +
					config.outline_top_padding
				)

		def sizeHint(self):
			return QSize(
				self.fontMetrics().width(self.line),
				self.fontMetrics().height()
				)

class events_class(QLabel):
	mouseHover = pyqtSignal(str, int, bool)
	redraw = pyqtSignal(bool, bool)

	def __init__(self, word, subs, skip = False, parent=None):
		super().__init__(word)
		self.setMouseTracking(True)
		self.word = word
		self.subs = subs
		self.skip = skip
		self.highlight = False

		self.setStyleSheet('background: transparent; color: transparent;')

	def highligting(self, color, underline_width):
		color = QColor(color)
		color = QColor(color.red(), color.green(), color.blue(), 200)
		painter = QPainter(self)

		if config.hover_underline:
			font_metrics = QFontMetrics(self.font())
			text_width = font_metrics.width(self.word)
			text_height = font_metrics.height()

			brush = QBrush(color)
			pen = QPen(brush, underline_width, Qt.SolidLine, Qt.RoundCap)
			painter.setPen(pen)
			if not self.skip:
				painter.drawLine(0, text_height - underline_width, text_width, text_height - underline_width)

		if config.hover_hightlight:
			x = y = 0
			y += self.fontMetrics().ascent()

			painter.setPen(color)
			painter.drawText(x, y + config.outline_top_padding - config.outline_bottom_padding, self.word)

	if config.outline_B:
		def paintEvent(self, evt: QPaintEvent):
			if self.highlight:
				self.highligting(config.hover_color, config.hover_underline_thickness)

	#####################################################

	def resizeEvent(self, event):
		text_height = self.fontMetrics().height()
		text_width = self.fontMetrics().width(self.word)

		self.setFixedSize(text_width, text_height + config.outline_bottom_padding + config.outline_top_padding)

	def enterEvent(self, event):
		if not self.skip:
			self.highlight = True
			self.repaint()
			config.queue_to_translate.put((self.word, event.globalX()))

	@pyqtSlot()
	def leaveEvent(self, event):
		if not self.skip:
			self.highlight = False
			self.repaint()

			config.scroll = {}
			self.mouseHover.emit('', 0, False)
			QApplication.restoreOverrideCursor()

	def wheel_scrolling(self, event):
		if event.y() > 0:
			return 'ScrollUp'
		if event.y():
			return 'ScrollDown'
		if event.x() > 0:
			return 'ScrollLeft'
		if event.x():
			return 'ScrollRight'

	def wheelEvent(self, event):
		for mouse_action in config.mouse_buttons:
			if self.wheel_scrolling(event.angleDelta()) == mouse_action[0]:
				if event.modifiers() == eval('Qt.%s' % mouse_action[1]):
					exec('self.%s(event)' % mouse_action[2])

	def mousePressEvent(self, event):
		for mouse_action in config.mouse_buttons:
			if 'Scroll' not in mouse_action[0]:
				if event.button() == eval('Qt.%s' % mouse_action[0]):
					if event.modifiers() == eval('Qt.%s' % mouse_action[1]):
						exec('self.%s(event)' % mouse_action[2])

	#####################################################

	def f_show_in_browser(self, event):
		config.avoid_resuming = True
		os.system(config.show_in_browser.replace('${word}', self.word))

	def f_auto_pause_options(self, event):
		if config.auto_pause == 2:
			config.auto_pause = 0
		else:
			config.auto_pause += 1
		mpv_message('auto_pause: %d' % config.auto_pause)

	def f_listen(self, event):
		listen(self.word, config.listen_via)

	@pyqtSlot()
	def f_subs_screen_edge_padding_decrease(self, event):
		config.subs_screen_edge_padding -= 5
		mpv_message('subs_screen_edge_padding: %d' % config.subs_screen_edge_padding)
		self.redraw.emit(False, True)

	@pyqtSlot()
	def f_subs_screen_edge_padding_increase(self, event):
		config.subs_screen_edge_padding += 5
		mpv_message('subs_screen_edge_padding: %d' % config.subs_screen_edge_padding)
		self.redraw.emit(False, True)

	@pyqtSlot()
	def f_font_size_decrease(self, event):
		config.style_subs = re.sub('font-size: (\d+)px;', lambda size: [ 'font-size: %dpx;' % ( int(size.group(1)) - 1 ), mpv_message('font: %s' % size.group(1)) ][0], config.style_subs, flags = re.I)
		self.redraw.emit(False, True)

	@pyqtSlot()
	def f_font_size_increase(self, event):
		config.style_subs = re.sub('font-size: (\d+)px;', lambda size: [ 'font-size: %dpx;' % ( int(size.group(1)) + 1 ), mpv_message('font: %s' % size.group(1)) ][0], config.style_subs, flags = re.I)
		self.redraw.emit(False, True)

	def f_auto_pause_min_words_decrease(self, event):
		config.auto_pause_min_words -= 1
		mpv_message('auto_pause_min_words: %d' % config.auto_pause_min_words)

	def f_auto_pause_min_words_increase(self, event):
		config.auto_pause_min_words += 1
		mpv_message('auto_pause_min_words: %d' % config.auto_pause_min_words)

	@pyqtSlot()
	def f_deepl_translation(self, event):
		self.mouseHover.emit(self.subs , event.globalX(), True)

	def f_save_word_to_file(self, event):
		if ( os.path.isfile(os.path.expanduser(config.save_word_to_file_fname)) and self.word not in [ x.strip() for x in open(os.path.expanduser(config.save_word_to_file_fname)).readlines() ] ) or not os.path.isfile(os.path.expanduser(config.save_word_to_file_fname)):
			print(self.word, file = open(os.path.expanduser(config.save_word_to_file_fname), 'a'))

	@pyqtSlot()
	def f_scroll_translations_up(self, event):
		if self.word in config.scroll and config.scroll[self.word] > 0:
			config.scroll[self.word] = config.scroll[self.word] - 1
		else:
			config.scroll[self.word] = 0
		self.mouseHover.emit(self.word, event.globalX(), False)

	@pyqtSlot()
	def f_scroll_translations_down(self, event):
		if self.word in config.scroll:
			config.scroll[self.word] = config.scroll[self.word] + 1
		else:
			config.scroll[self.word] = 1
		self.mouseHover.emit(self.word, event.globalX(), False)

class main_class(QWidget):
	def __init__(self):
		super().__init__()

		self.thread_subs = QThread()
		self.obj = thread_subtitles()
		self.obj.update_subtitles.connect(self.render_subtitles)
		self.obj.moveToThread(self.thread_subs)
		self.thread_subs.started.connect(self.obj.main)
		self.thread_subs.start()

		self.thread_translations = QThread()
		self.obj2 = thread_translations()
		self.obj2.get_translations.connect(self.render_popup)
		self.obj2.moveToThread(self.thread_translations)
		self.thread_translations.started.connect(self.obj2.main)
		self.thread_translations.start()

		# start the forms
		self.subtitles_base()
		self.subtitles_base2()
		self.popup_base()

	def clearLayout(self, layout):
		if layout == 'subs':
			layout = self.subtitles_vbox
			self.subtitles.hide()
		elif layout == 'subs2':
			layout = self.subtitles_vbox2
			self.subtitles2.hide()
		elif layout == 'popup':
			layout = self.popup_vbox
			self.popup.hide()

		if layout is not None:
			while layout.count():
				item = layout.takeAt(0)
				widget = item.widget()

				if widget is not None:
					widget.deleteLater()
				else:
					self.clearLayout(item.layout())

	def subtitles_base(self):
		self.subtitles = QFrame()
		self.subtitles.setAttribute(Qt.WA_TranslucentBackground)
		self.subtitles.setWindowFlags(Qt.X11BypassWindowManagerHint)
		self.subtitles.setStyleSheet(config.style_subs)

		self.subtitles_vbox = QVBoxLayout(self.subtitles)
		self.subtitles_vbox.setSpacing(config.subs_padding_between_lines)
		self.subtitles_vbox.setContentsMargins(0, 0, 0, 0)

	def subtitles_base2(self):
		self.subtitles2 = QFrame()
		self.subtitles2.setAttribute(Qt.WA_TranslucentBackground)
		self.subtitles2.setWindowFlags(Qt.X11BypassWindowManagerHint)
		self.subtitles2.setStyleSheet(config.style_subs)

		self.subtitles_vbox2 = QVBoxLayout(self.subtitles2)
		self.subtitles_vbox2.setSpacing(config.subs_padding_between_lines)
		self.subtitles_vbox2.setContentsMargins(0, 0, 0, 0)

		if config.pause_during_translation_B:
			self.subtitles2.enterEvent = lambda event : [mpv_pause(), setattr(config, 'block_popup', False)][0]
			self.subtitles2.leaveEvent = lambda event : [mpv_resume(), setattr(config, 'block_popup', True)][0] if not config.avoid_resuming else [setattr(config, 'avoid_resuming', False), setattr(config, 'block_popup', True)][0]

	def popup_base(self):
		self.popup = QFrame()
		self.popup.setAttribute(Qt.WA_TranslucentBackground)
		self.popup.setWindowFlags(Qt.X11BypassWindowManagerHint)
		self.popup.setStyleSheet(config.style_popup)

		self.popup_inner = QFrame()
		outer_box = QVBoxLayout(self.popup)
		outer_box.addWidget(self.popup_inner)

		self.popup_vbox = QVBoxLayout(self.popup_inner)
		self.popup_vbox.setSpacing(0)

	def render_subtitles(self, hide = False, redraw = False):
		if hide or not len(subs):
			try:
				self.subtitles.hide()
				self.subtitles2.hide()
			finally:
				return

		if redraw:
			self.subtitles.setStyleSheet(config.style_subs)
			self.subtitles2.setStyleSheet(config.style_subs)
		else:
			self.clearLayout('subs')
			self.clearLayout('subs2')

			if hasattr(self, 'popup'):
				self.popup.hide()

			# if subtitle consists of one overly long line - split into two
			if config.split_long_lines_B and len(subs.split('\n')) == 1 and len(subs.split(' ')) > config.split_long_lines_words_min - 1:
				subs2 = split_long_lines(subs)
			else:
				subs2 = subs

			subs2 = re.sub(' +', ' ', subs2).strip()

			##############################

			for line in subs2.split('\n'):
				line2 = ' %s ' % line.strip()
				ll = drawing_layer(line2, subs2)

				hbox = QHBoxLayout()
				hbox.setContentsMargins(0, 0, 0, 0)
				hbox.setSpacing(0)
				hbox.addStretch()
				hbox.addWidget(ll)
				hbox.addStretch()
				self.subtitles_vbox.addLayout(hbox)

				####################################

				hbox = QHBoxLayout()
				hbox.setContentsMargins(0, 0, 0, 0)
				hbox.setSpacing(0)
				hbox.addStretch()

				if config.R2L_from_B:
					line2 = line2[::-1]

				line2 += '\00'
				word = ''
				for smbl in line2:
					if smbl.isalpha():
						word += smbl
					else:
						if len(word):
							if config.R2L_from_B:
								word = word[::-1]

							ll = events_class(word, subs2)
							ll.mouseHover.connect(self.render_popup)
							ll.redraw.connect(self.render_subtitles)

							hbox.addWidget(ll)
							word = ''

						if smbl != '\00':
							ll = events_class(smbl, subs2, skip = True)
							hbox.addWidget(ll)

				hbox.addStretch()
				self.subtitles_vbox2.addLayout(hbox)

		self.subtitles.adjustSize()
		self.subtitles2.adjustSize()

		w = self.subtitles.geometry().width()
		h = self.subtitles.height = self.subtitles.geometry().height()

		x = (config.screen_width/2) - (w/2)

		if config.subs_top_placement_B:
			y = config.subs_screen_edge_padding
		else:
			y = config.screen_height - config.subs_screen_edge_padding - h

		self.subtitles.setGeometry(x, y, 0, 0)
		self.subtitles.show()

		self.subtitles2.setGeometry(x, y, 0, 0)
		self.subtitles2.show()

	def render_popup(self, text, x_cursor_pos, is_line):
		if text == '':
			if hasattr(self, 'popup'):
				self.popup.hide()
			return

		self.clearLayout('popup')

		if is_line:
			QApplication.setOverrideCursor(Qt.WaitCursor)
			line = deepl(text)
			if config.split_long_lines_B and len(line.split('\n')) == 1 and len(line.split(' ')) > config.split_long_lines_words_min - 1:
				line = split_long_lines(line)

			ll = QLabel(line)
			ll.setObjectName("first_line")
			self.popup_vbox.addWidget(ll)
		else:
			word = text

			for translation_function_name_i, translation_function_name in enumerate(config.translation_function_names):
				pairs, word_descr = globals()[translation_function_name](word)

				if not len(pairs):
					pairs = [['', '[Not found]']]
					#return

				# ~pairs = [ [ str(i) + ' ' + pair[0], pair[1] ] for i, pair in enumerate(pairs) ]

				if word in config.scroll:
					if len(pairs[config.scroll[word]:]) > config.number_of_translations:
						pairs = pairs[config.scroll[word]:]
					else:
						pairs = pairs[-config.number_of_translations:]
						if len(config.translation_function_names) == 1:
							config.scroll[word] -= 1

				for i1, pair in enumerate(pairs):
					if i1 == config.number_of_translations:
						break

					if config.split_long_lines_in_popup_B:
						pair[0] = split_long_lines(pair[0], max_symbols_per_line = config.split_long_lines_in_popup_symbols_min)
						pair[1] = split_long_lines(pair[1], max_symbols_per_line = config.split_long_lines_in_popup_symbols_min)

					if pair[0] == '-':
						pair[0] = ''
					if pair[1] == '-':
						pair[1] = ''

					# ~if config.R2L_from_B:
						# ~pair[0] = pair[0][::-1]
					# ~if config.R2L_to_B:
						# ~pair[1] = pair[1][::-1]

					if pair[0] != '':
						# to emphasize the exact form of the word
						# to ignore case on input and match it on output
						chnks = re.split(word, pair[0], flags = re.I)
						exct_words = re.findall(word, pair[0], flags = re.I)

						hbox = QHBoxLayout()
						hbox.setContentsMargins(0, 0, 0, 0)

						for i2, chnk in enumerate(chnks):
							if len(chnk):
								ll = QLabel(chnk)
								ll.setObjectName("first_line")
								hbox.addWidget(ll)
							if i2 + 1 < len(chnks):
								ll = QLabel(exct_words[i2])
								ll.setObjectName("first_line_emphasize_word")
								hbox.addWidget(ll)

						# filling the rest of the line with empty bg
						ll = QLabel()
						ll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
						hbox.addWidget(ll)

						self.popup_vbox.addLayout(hbox)

					if pair[1] != '':
						ll = QLabel(pair[1])
						ll.setObjectName("second_line")
						self.popup_vbox.addWidget(ll)

						# padding
						ll = QLabel()
						ll.setStyleSheet("font-size: 6px;")
						self.popup_vbox.addWidget(ll)

				if len(word_descr[0]):
					ll = QLabel(word_descr[0])
					ll.setProperty("morphology", word_descr[1])
					ll.setAlignment(Qt.AlignRight)
					self.popup_vbox.addWidget(ll)

				# delimiter between dictionaries
				if translation_function_name_i + 1 < len(config.translation_function_names):
					ll = QLabel()
					ll.setObjectName("delimiter")
					self.popup_vbox.addWidget(ll)

		self.popup_inner.adjustSize()
		self.popup.adjustSize()

		w = self.popup.geometry().width()
		h = self.popup.geometry().height()

		if w > config.screen_width:
			w = config.screen_width - 20

		if not is_line:
			if w < config.screen_width / 3:
				w = config.screen_width / 3

		if x_cursor_pos == -1:
			x = (config.screen_width/2) - (w/2)
		else:
			x = x_cursor_pos - w/5
			if x+w > config.screen_width:
				x = config.screen_width - w

		if config.subs_top_placement_B:
			y = self.subtitles.height + config.subs_screen_edge_padding
		else:
			y = config.screen_height - config.subs_screen_edge_padding - self.subtitles.height - h

		self.popup.setGeometry(x, y, w, 0)
		self.popup.show()

		QApplication.restoreOverrideCursor()

if __name__ == "__main__":
	print('[py part] Starting interSubs ...')

	try:
		os.mkdir('urls')
	except:
		pass

	if 'tab_divided_dict' in config.translation_function_names:
		offdict = { x.split('\t')[0].strip().lower() : x.split('\t')[1].strip() for x in open(os.path.expanduser(config.tab_divided_dict_fname)).readlines() if '\t' in x }

	mpv_socket = sys.argv[1]
	sub_file = sys.argv[2]
	# sub_file = '/tmp/mpv_sub_'
	# mpv_socket = '/tmp/mpv_socket_'

	subs = ''

	app = QApplication(sys.argv)

	config.avoid_resuming = False
	config.block_popup = False
	config.scroll = {}
	config.queue_to_translate = queue.Queue()
	config.screen_width = app.primaryScreen().size().width()
	config.screen_height = app.primaryScreen().size().height()

	form = main_class()
	app.exec_()
