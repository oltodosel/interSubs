#! /usr/bin/env python3

# v. 1.12
# Interactive subtitles for `mpv` for language learners.

import os, subprocess, sys
import random, re, time
import requests
from tkinter import *

from urllib.parse import quote
from json import loads

import warnings
from six.moves import urllib

import calendar
import math
import base64

import numpy
from bs4 import BeautifulSoup

def render_subtitles():
	global frame, subs_hight, scroll

	try:
		popup.destroy()
	except:
		pass
	try:
		frame.destroy()
	except:
		pass

	if not len(subs):
		return

	scroll = {}

	frame = Frame(window)
	frame.configure(background = bg_color1, padx = 3, pady = 0)
	frame.pack()
	frame.bind("<Button>", wheel_ev)

	if pause_during_translation:
		frame.bind("<Enter>", mpv_pause)
		frame.bind("<Leave>", mpv_resume)

	# putting first line without its own frame won't center it when second line is longer
	frame1 = Frame(frame)
	frame1.configure(background = bg_color1)
	frame1.pack()
	frame2 = Frame(frame)
	frame2.configure(background = bg_color1)
	frame2.pack()

	# if subtitle consists of one overly long line - split into two
	if split_long_lines and len(subs.split('\n')) == 1 and len(subs.split(' ')) > split_long_lines_words_min - 1:
		subs2 = ' '.join(numpy.array_split(subs.split(' '), 2)[0]) + '\n' + ' '.join(numpy.array_split(subs.split(' '), 2)[1])
	else:
		subs2 = subs

	subs2 = re.sub(' +', ' ', subs2)

	for i1, line in enumerate(subs2.split('\n')):
		line = line.strip()
		line2 = ''

		if R2L_from:
			# since tk doesn't support right-to-left text
			# might botch some text
			try:
				line2 = re.findall('(?!%)\W+$',line)[0]
			except:
				pass

			line2 += re.sub('^\W+|(?!%)\W+$','',line)

			try:
				line2 += re.findall('^\W+',line)[0]
			except:
				pass

			line2 = line2[::-1]
			# reversing back l2r chunks
			line2 = re.sub('[0-9a-zA-Z%\$-]{2,}', lambda x: x.group(0)[::-1], line2)
		else:
			line2 = line

		line2 += '\00'
		word = ''
		for smbl in line2:
			if smbl.isalpha():
				word += smbl
			else:
				if len(word):
					if not i1:
						bb = Button(frame1)
					else:
						bb = Button(frame2)

					fgc = font_color1
					if colorize_nouns and word.istitle() and stripsd3(word) in de_dict:
						if de_dict[stripsd3(word)] == 'Masc':
							fgc = font_color8
						elif de_dict[stripsd3(word)] == 'Fem':
							fgc = font_color9
						elif de_dict[stripsd3(word)] == 'Neut':
							fgc = font_color10

					bb.configure(text = word, font = font1, borderwidth = 0, padx = 0, pady = 0, relief = FLAT, background = bg_color1, foreground = fgc, highlightthickness = 0)

					if R2L_from:
						word = word[::-1]

					bb.pack(side = LEFT)
					bb.bind("<Enter>", lambda event, arg = word: render_popup(event, arg))
					bb.bind("<Leave>", lambda event: popup.destroy())
					bb.bind("<Button>", lambda event, arg = word: wheel_ev(event, arg))

					word = ''

				if smbl != '\00':
					if not i1:
						Label(frame1, text = smbl, font = font1, borderwidth = 0, padx = 0, pady = 0, relief = FLAT, background = bg_color1, foreground = font_color1, highlightthickness = 0).pack(side = LEFT)
					else:
						Label(frame2, text = smbl, font = font1, borderwidth = 0, padx = 0, pady = 0, relief = FLAT, background = bg_color1, foreground = font_color1, highlightthickness = 0).pack(side = LEFT)

	window.update_idletasks()

	w = window.winfo_width()
	h = subs_hight = window.winfo_height()

	x = (ws/2) - (w/2)
	y = hs - subs_bottom_padding - h

	beysc()
	window.geometry('%dx%d+%d+%d' % (w, h, x, y))
	window.geometry('')

def render_popup(event, word):
	global popup, scroll

	try:
		popup.geometry('%dx%d+%d+%d' % (0, 0, 0, 0))
	except:
		pass

	pairs, word_descr = globals()[translation_function_name](word)

	if not len(pairs):
		#pairs = [['[Not found]', '']]
		return

	#pairs = [ [ str(i) + ' ' + pair[0], pair[1] ] for i, pair in enumerate(pairs) ]

	if randomize_translations:
		tmp_pairs = pairs[1:]
		random.shuffle(tmp_pairs)
		pairs = [pairs[0]] + tmp_pairs
	elif word in scroll:
		if len(pairs[scroll[word]:]) > number_of_translations:
			pairs = pairs[scroll[word]:]
		else:
			pairs = pairs[-number_of_translations:]
			scroll[word] = scroll[word] - 1

	popup = Toplevel(root)
	popup.geometry('+%d+%d' % (ws+999, hs+999))
	popup.overrideredirect(1)
	popup.configure(background = bg_color2, padx = popup_ext_n_int_padding, pady = popup_ext_n_int_padding)

	wrplgth = ws - ws/3

	for i, pair in enumerate(pairs):
		if i == number_of_translations:
			break

		if pair[0] == '-':
			pair[0] = ''
		if pair[1] == '-':
			pair[1] = ''

		anchor1 = "w"
		anchor2 = "w"
		if R2L_from:
			pair[0] = pair[0][::-1]
			anchor1 = "e"
		if R2L_to:
			pair[1] = pair[1][::-1]
			anchor2 = "e"

		# to emphasize the exact form of the word
		psdo_label = Frame(popup)
		psdo_label.pack(side = "top", anchor = anchor1)
		psdo_label.configure(borderwidth = 0, padx = popup_ext_n_int_padding, pady = 0, background = bg_color2)

		# to ignore case on input and match it on output
		chnks = re.split(word, pair[0], flags=re.I)
		exct_words = re.findall(word, pair[0], flags=re.I)

		for i, chnk in enumerate(chnks):
			if len(chnk):
				Label(psdo_label, text = chnk, font = font2, borderwidth = 0, padx = 0, pady = 0, background = bg_color2, foreground = font_color2, highlightthickness = 0, wraplength = wrplgth, justify = "left").pack(side = "left", anchor = "w")
			if i + 1 < len(chnks):
				Label(psdo_label, text = exct_words[i], font = font2 + ('underline',), borderwidth = 0, padx = 0, pady = 0, background = bg_color2, foreground = font_color2, highlightthickness = 0, wraplength = wrplgth, justify = "left").pack(side = "left", anchor = "w")

		Label(popup, text = pair[1], font = font2, borderwidth = 0, padx = popup_ext_n_int_padding, pady = 0, background = bg_color2, foreground = font_color3, highlightthickness = 0, wraplength = wrplgth, justify = "left").pack(side = "top", anchor = anchor2)

		# couldn't control padding of one side, thus:
		Label(popup, pady = 0, background = bg_color2).pack(side = "top")

	if len(word_descr[0]):
		if word_descr[1] == 'm':
			word_descr_color = font_color5
		elif word_descr[1] == 'f':
			word_descr_color = font_color6
		elif word_descr[1] == 'nt':
			word_descr_color = font_color7
		else:
			word_descr_color = font_color4

		Label(popup, text = word_descr[0], font = font3, padx = popup_ext_n_int_padding, pady = 0, background = bg_color2, foreground = word_descr_color, wraplength = wrplgth, justify = "left").pack(side = "top", anchor = "e")

	popup.update_idletasks()

	w = popup.winfo_width() + popup_ext_n_int_padding
	h = popup.winfo_height() + popup_ext_n_int_padding

	if w > ws - popup_ext_n_int_padding * 2:
		w = ws - popup_ext_n_int_padding * 2

	x = event.x_root-w/5
	if x+w > ws-popup_ext_n_int_padding:
		x = ws - w - popup_ext_n_int_padding

	y = hs - subs_bottom_padding - subs_hight - h - popup_ext_n_int_padding

	popup.geometry('%dx%d+%d+%d' % (w, h, x, y))

# returns ([[word, translation]..], [morphology = '', gender = ''])
# pons.com
def pons(word):
	if lang_from + lang_to in pons_combos:
		url = 'http://en.pons.com/translate?q=%s&l=%s%s&in=%s' % (quote(word), lang_from, lang_to, lang_from)
	else:
		url = 'http://en.pons.com/translate?q=%s&l=%s%s&in=%s' % (quote(word), lang_to, lang_from, lang_from)

	pairs = []
	try:
		if save_translations:
			p = open('urls/' + url.replace('/',"-")).read().split('=====/////-----')
			try:
				word_descr = p[1].strip()
			except:
				word_descr = ''

			for pi in p[0].strip().split('\n\n'):
				pi = pi.split('\n')
				pairs.append([pi[0], pi[1]])
		else:
			error
	except:
		p = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text

		soup = BeautifulSoup(p, "lxml")
		trs = soup.find_all('dl')

		for tr in trs[1:]:
			tr1 = tr.find('dt').find('div', class_="source").get_text()
			tr1 = re.sub('\n|\r|\t', ' ', tr1)
			tr1 = re.sub(' +', ' ', tr1).strip()

			tr2 = tr.find('dd').find('div', class_="target").get_text()
			tr2 = re.sub('\n|\r|\t', ' ', tr2)
			tr2 = re.sub(' +', ' ', tr2).strip()

			pairs.append([tr1, tr2])

			if number_of_translations_to_save and len(pairs) > number_of_translations_to_save:
				break

		try:
			word_descr = soup.find_all('h2', class_ = '')
			word_descr = re.sub('\n|\r|\t', ' ', word_descr[0].get_text())
			word_descr = re.sub(' +', ' ', word_descr).replace('&lt;', '<').replace('&gt;', '>').replace(' · ', '·').replace(' , ', ', ').strip()
		except:
			word_descr = ''

		if save_translations:
			print('\n\n'.join(e[0] + '\n' + e[1] for e in pairs), file=open('urls/' + url.replace('/',"-"), 'a'))
			print('\n'+'=====/////-----'+'\n', file=open('urls/' + url.replace('/',"-"), 'a'))
			print(word_descr, file=open('urls/' + url.replace('/',"-"), 'a'))

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

# translate.google.com
def mtranslate_google(word):
	import html.parser
	import urllib.request
	import urllib.parse

	agent = {'User-Agent':
	"Mozilla/4.0 (\
	compatible;\
	MSIE 6.0;\
	Windows NT 5.1;\
	SV1;\
	.NET CLR 1.1.4322;\
	.NET CLR 2.0.50727;\
	.NET CLR 3.0.04506.30\
	)"}

	def unescape(text):
		parser = html.parser.HTMLParser()
		return (parser.unescape(text))

	def translate(to_translate, to_language="auto", from_language="auto"):
		base_link = "http://translate.google.com/m?hl=%s&sl=%s&q=%s"

		to_translate = urllib.parse.quote(to_translate)
		link = base_link % (to_language, from_language, to_translate)
		request = urllib.request.Request(link, headers=agent)
		raw_data = urllib.request.urlopen(request).read()

		data = raw_data.decode("utf-8")
		expr = r'class="t0">(.*?)<'
		re_result = re.findall(expr, data)

		if (len(re_result) == 0):
			result = ""
		else:
			result = unescape(re_result[0])
		return (result)

	return [[word, translate(word, lang_to, lang_from)]], ['', '']

# reverso.net
def reverso(word):
	if not lang_from in reverso_combos and not lang_to in reverso_combos:
		return [['Language code is not correct.', '']], ['', '']

	url = 'http://context.reverso.net/translation/%s-%s/%s' % (reverso_combos[lang_from].lower(), reverso_combos[lang_to].lower(), quote(word))

	pairs = []
	try:
		if save_translations:
			p = open('urls/' + url.replace('/',"-")).read().split('=====/////-----')

			for pi in p[0].strip().split('\n\n'):
				pi = pi.split('\n')
				pairs.append([pi[0], pi[1]])
		else:
			error
	except:
		p = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text

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

		if save_translations:
			print('\n\n'.join(e[0] + '\n' + e[1] for e in pairs), file=open('urls/' + url.replace('/',"-"), 'a'))
			print('\n'+'=====/////-----'+'\n', file=open('urls/' + url.replace('/',"-"), 'a'))

	return pairs, ['', '']

def wheel_ev(event, word = ''):
	global subs_bottom_padding, font1, scroll, auto_pause, auto_pause_min_words

	# event.state: Ctrl == 4, Shift == 1, None == 0

	if event.num == 1:
		os.system(external_dictionary_cmd_on_click.replace('${word}', word))
	elif event.num == 2:
		if auto_pause == 2:
			auto_pause = 0
		else:
			auto_pause += 1

		mpv_message('auto_pause: ' + str(auto_pause))
	elif event.num == 3:
		listen(word, listen_via)
	elif event.num == 4:
		if event.state == 0:
			if save_translations:
				if word in scroll and scroll[word] > 0:
					scroll[word] = scroll[word] - 1
				else:
					scroll[word] = 0
				render_popup(event, word)
		elif event.state == 1:
			font1 = (font1[0], font1[1] + 1)
			mpv_message('font1: ' + str(font1))
			beysc()
			render_subtitles()
		elif event.state == 4:
			subs_bottom_padding += 5
			mpv_message('subs_bottom_padding: ' + str(subs_bottom_padding))
			beysc()
			render_subtitles()
	elif event.num == 5:
		if event.state == 0:
			if save_translations:
				if word in scroll:
					scroll[word] = scroll[word] + 1
				else:
					scroll[word] = 1
				render_popup(event, word)
		elif event.state == 1:
			font1 = (font1[0], font1[1] - 1)
			mpv_message('font1: ' + str(font1))
			beysc()
			render_subtitles()
		elif event.state == 4:
			subs_bottom_padding -= 5
			mpv_message('subs_bottom_padding: ' + str(subs_bottom_padding))
			beysc()
			render_subtitles()
	elif event.num == 6:
		auto_pause_min_words = auto_pause_min_words - 1
		mpv_message('auto_pause_min_words: ' + str(auto_pause_min_words))
	elif event.num == 7:
		auto_pause_min_words = auto_pause_min_words + 1
		mpv_message('auto_pause_min_words: ' + str(auto_pause_min_words))

def listen(word, type = 'gtts'):
	if type == 'pons':
		if lang_from + lang_to in pons_combos:
			url = 'http://en.pons.com/translate?q=%s&l=%s%s&in=%s' % (quote(word), lang_from, lang_to, lang_from)
		else:
			url = 'http://en.pons.com/translate?q=%s&l=%s%s&in=%s' % (quote(word), lang_to, lang_from, lang_from)

		p = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
		x = re.findall('<dl id="([a-zA-Z0-9]*?)" class="dl-horizontal kne(.*?)</dl>', p, re.DOTALL)
		x2 = re.findall('class="audio tts trackable trk-audio" data-pons-lang="(.*?)"', x[0][1])

		for l in x2:
			if lang_from in l:
				mp3 = 'http://sounds.pons.com/audio_tts/%s/%s' % (l, x[0][0])
				break

		os.system('(cd /tmp; wget ' + mp3 + '; mpv --load-scripts=no --loop=1 --volume=40 --force-window=no ' + mp3.split('/')[-1] + '; rm ' + mp3.split('/')[-1] + ') &')
	elif type == 'gtts':
		gTTS(text = word, lang = lang_from, slow = False).save('/tmp/gtts_word.mp3')
		os.system('(mpv --load-scripts=no --loop=1 --volume=75 --force-window=no ' + '/tmp/gtts_word.mp3' + '; rm ' + '/tmp/gtts_word.mp3' + ') &')
	elif type == 'forvo':
		url = 'https://forvo.com/word/%s/%s/' % (lang_from, quote(word))

		try:
			data = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text

			soup = BeautifulSoup(data, "lxml")
			trs = soup.find_all('article', class_ = 'pronunciations')[0].find_all('a', class_ = 'play')

			for tr in trs[:2]:
				tr = tr['onclick']
				tr = re.findall('Play\((.*?)\)', tr)[0]
				tr = tr.split(',')[4].replace("'", '')
				tr = base64.b64decode(tr)
				tr = tr.decode("utf-8")
				print(tr)

				os.system('(mpv --load-scripts=no --loop=2 --volume=111 --force-window=no https://audio00.forvo.com/audios/mp3/%s) &' % tr)
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

		timestamp = calendar.timegm(time.gmtime())
		hours = int(math.floor(timestamp / 3600))

		response = requests.get("https://translate.google.com/")
		line = response.text.split('\n')[-1]

		tkk_expr = re.search(".*?(TKK=.*?;)W.*?", line).group(1)
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
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
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

def mpv_pause(e = None):
	os.system('echo \'{ "command": ["set_property", "pause", true] }\' | socat - "' + mpv_socket + '" > /dev/null')

def mpv_resume(e = None):
	os.system('echo \'{ "command": ["set_property", "pause", false] }\' | socat - "' + mpv_socket + '" > /dev/null')

def mpv_pause_status():
	stdoutdata = subprocess.getoutput('echo \'{ "command": ["get_property", "pause"] }\' | socat - "' + mpv_socket + '"')

	try:
		return loads(stdoutdata)['data']
	except:
		return mpv_pause_status()

def mpv_fullscreen_status():
	#return 1
	stdoutdata = subprocess.getoutput('echo \'{ "command": ["get_property", "fullscreen"] }\' | socat - "' + mpv_socket + '"')

	try:
		return loads(stdoutdata)['data']
	except:
		return mpv_fullscreen_status()

def mpv_message(message, timeout = 3000):
	os.system('echo \'{ "command": ["show-text", "' + message + '", "' + str(timeout) + '"] }\' | socat - "' + mpv_socket + '" > /dev/null')

# render beyond the screen
def beysc():
	window.geometry('+%d+%d' % (ws+999, hs+999))
	window.update_idletasks()

def stripsd2(phrase):
	return ''.join(e for e in phrase.strip().lower() if e == ' ' or (e.isalnum() and not e.isdigit())).strip()

def stripsd3(word):
	return ''.join(e for e in word.strip() if e.isalnum() and not e.isdigit())

#########################################

pth = os.path.expanduser('~/.config/mpv/scripts/')
os.chdir(pth)
exec(open('interSubs.conf.py').read())

pons_combos = ['enes', 'enfr', 'deen', 'enpl', 'ensl', 'defr', 'dees', 'deru', 'depl', 'desl', 'deit', 'dept', 'detr', 'deel', 'dela', 'espl', 'frpl', 'itpl', 'plru', 'essl', 'frsl', 'itsl', 'enit', 'enpt', 'enru', 'espt', 'esfr', 'delb', 'dezh', 'enzh', 'eszh', 'frzh', 'denl', 'arde', 'aren', 'dade', 'csde', 'dehu', 'deno', 'desv', 'dede', 'dedx']

reverso_combos = {'ar':'Arabic', 'de':'German', 'en':'English', 'es':'Spanish', 'fr':'French', 'he':'Hebrew', 'it':'Italian', 'nl':'Dutch', 'pl':'Polish', 'pt':'Portuguese', 'ro':'Romanian', 'ru':'Russian'}

if save_translations:
	try:
		os.mkdir('urls')
	except:
		pass

if __name__ == "__main__":
	print('[py part] Starting interSubs ...')

	if colorize_nouns:
		de_dict = { x.split('\t')[0] : x.split('\t')[2] for x in open(colorization_dict).readlines() }

	mpv_socket = sys.argv[1]
	sub_file = sys.argv[2]

	#########################################

	root = Tk()
	root.withdraw()								# hide first window
	window = Toplevel(root)

	ws = window.winfo_screenwidth()				# get screen width and height
	hs = window.winfo_screenheight()

	window.overrideredirect(1)					# remove border
	window.configure(background = bg_color1)

	beysc()

	subs = ''
	scroll = {}
	was_hidden = 0
	inc = 0
	auto_pause_2_ind = 0
	while 1:
		time.sleep(update_time)
		window.update()

		# hide subs when mpv isn't in focus or in fullscreen
		if inc * update_time > focus_checking_time - 0.0001:
			while 'mpv' not in subprocess.getoutput('xdotool getwindowfocus getwindowname') or (hide_when_not_fullscreen and not mpv_fullscreen_status()):
				if not was_hidden:
					try:
						popup.destroy()
					except:
						pass
					beysc()
					was_hidden = 1
				else:
					time.sleep(focus_checking_time)
			inc = 0
		inc += 1

		if was_hidden:
			was_hidden = 0
			render_subtitles()
			continue

		try:
			tmp_file_subs = open(sub_file).read()
		except:
			continue

		if extend_subs_duration2max and not len(tmp_file_subs):
			continue

		# automatically switch into Hebrew language if it's detected
		if lang_from != 'he' and any((c in set('קראטוןםפשדגכעיחלךףזסבהנמצתץ')) for c in tmp_file_subs):
			lang_from = 'he'
			# http://culmus.sourceforge.net/summary.html
			font1 = (random.choice(['Miriam', 'Yehuda', 'Ellinia', 'Drugulin', 'Caladings', 'David', 'Frank Ruehl', 'Nachlieli', 'Miriam Mono', 'Shofar', 'Hadasim', 'Simple', 'Stam']), 44)
			R2L_from = 1
			translation_function_name = 'reverso'
			listen_via = 'forvo'

			os.system('notify-send -i none -t 1111 "He"')
			os.system('notify-send -i none -t 1111 "%s"' % str(font1))

		while tmp_file_subs != subs:
			if auto_pause == 2:
				if not auto_pause_2_ind and len(re.sub(' +', ' ', stripsd2(subs.replace('\n', ' '))).split(' ')) > auto_pause_min_words - 1 and not mpv_pause_status():
					mpv_pause()
					auto_pause_2_ind = 1

				if auto_pause_2_ind and mpv_pause_status():
					break

				auto_pause_2_ind = 0

			subs = tmp_file_subs
			beysc()
			render_subtitles()

			if auto_pause == 1:
				if len(re.sub(' +', ' ', stripsd2(subs.replace('\n', ' '))).split(' ')) > auto_pause_min_words - 1:
					mpv_pause()

			break
