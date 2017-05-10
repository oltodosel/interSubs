#! /usr/bin/env python3

# v. 1.6
# Interactive subtitles for `mpv` for language learners.

import os, subprocess, sys
import requests
from tkinter import *
from time import sleep
from urllib.parse import quote
from random import shuffle
import subprocess
from json import loads

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
	frame.configure(background = bg_color1, padx = 4, pady = 0)
	frame.pack()

	frame.bind("<Enter>", mpv_pause)
	frame.bind("<Leave>", mpv_resume)
	frame.bind("<Button-4>", wheel_ev)		# binding frame to cover whitespaces
	frame.bind("<Button-5>", wheel_ev)
	frame.bind("<Button-2>", wheel_click)

	# putting first line without its own frame won't center it when second line is longer
	frame1 = Frame(frame)
	frame1.pack()
	frame2 = Frame(frame)
	frame2.pack()

	for i1, line in enumerate(subs.split('\n')):
		for i2, word in enumerate(line.split(' ')):
			if i2 != len(line.split(' ')) - 1:
				word = word + ' '

			if not i1:
				bb = Button(frame1)
			else:
				bb = Button(frame2)

			bb.configure(text = word, font = font1, borderwidth = 0, padx = 0, pady = 0, relief = FLAT, background = bg_color1 ,foreground = font_color1, highlightthickness = 0)
			word = stripsd(word)
			bb.pack(side = LEFT)
			bb.bind("<Enter>", lambda event, arg = word: render_popup(event, arg))
			bb.bind("<Leave>", lambda event: popup.destroy())
			bb.bind("<Button-1>", lambda event, arg = word: os.system(external_dictionary_cmd_on_click.replace('${word}', arg)))
			bb.bind("<Button-2>", wheel_click)
			bb.bind("<Button-3>", lambda event, arg = word: listen(arg))
			bb.bind("<Button-4>", lambda event, arg = word: wheel_ev(event, arg))
			bb.bind("<Button-5>", lambda event, arg = word: wheel_ev(event, arg))

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
		shuffle(tmp_pairs)
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

		# to emphasize the exact form of the word
		psdo_label = Frame(popup)
		psdo_label.pack(side = "top", anchor = "w")
		psdo_label.configure(borderwidth = 0, padx = popup_ext_n_int_padding, pady = 0, background = bg_color2)

		# to ignore case on input and match it on output
		chnks = re.split(word, pair[0], flags=re.I)
		exct_words = re.findall(word, pair[0], flags=re.I)

		for i, chnk in enumerate(chnks):
			if len(chnk):
				Label(psdo_label, text = chnk, font = font2, borderwidth = 0, padx = 0, pady = 0, background = bg_color2, foreground = font_color2, highlightthickness = 0, wraplength = wrplgth, justify = "left").pack(side = "left", anchor = "w")
			if i + 1 < len(chnks):
				Label(psdo_label, text = exct_words[i], font = font2 + ('underline',), borderwidth = 0, padx = 0, pady = 0, background = bg_color2, foreground = font_color2, highlightthickness = 0, wraplength = wrplgth, justify = "left").pack(side = "left", anchor = "w")

		Label(popup, text = pair[1], font = font2, borderwidth = 0, padx = popup_ext_n_int_padding, pady = 0, background = bg_color2, foreground = font_color3, highlightthickness = 0, wraplength = wrplgth, justify = "left").pack(side = "top", anchor = "w")

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
		p = p.replace('&#39;',"'")
		p = p.replace('<acronym title="informal">fam</acronym>', ' ')
		p = re.sub('<span class="flag .*?</a>', ' ', p)

		x = re.findall('<dt>(.*?)</dt>.*?<dd>(.*?)</dd>', p, re.DOTALL)

		for c in x:
			f1 = c[0].replace('\n', ' ')
			f1 = re.sub('<acronym(.*?)>(.*?)</acronym>', '\g<2>', f1)
			f1 = re.sub('<(.*?)>', '', f1)
			f1 = re.sub(' +', ' ', f1)
			f1 = f1.strip()
			###
			f2 = c[1]
			f2 = re.sub('<acronym(.*?)>(.*?)</acronym>', '\g<2>', f2)
			f2 = re.sub('<(.*?)>', '', f2)
			f2 = f2.strip()
			f2 = f2.split('\n')[0]
			f2 = re.sub(' +', ' ', f2)
			f2 = f2.strip()

			pairs.append([f1, f2])

			if number_of_translations_to_save and len(pairs) > number_of_translations_to_save:
				break
		try:
			p = p.replace('<span class="roman">I.</span>',"")
			y = re.findall('<div class="entry.*?<h2>(.*?)</h2>', p, re.DOTALL)
			word_descr = re.sub(' +', ' ', re.sub('<(.*?)>|\n|\r|\t| ', ' ', y[0]).replace('&lt;', '<').replace('&gt;', '>')).replace(' · ', '·').replace(' , ', ', ').strip()
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

def wheel_ev(event, word = ''):
	global subs_bottom_padding, font1, scroll

	# event.state: Ctrl == 4, Shift == 1, None == 0
	if event.state == 0:
		if save_translations:
			if event.num == 4:
				if word in scroll and scroll[word] > 0:
					scroll[word] = scroll[word] - 1
				else:
					scroll[word] = 0
			else:
				if word in scroll:
					scroll[word] = scroll[word] + 1
				else:
					scroll[word] = 1

			render_popup(event, word)
			return
	elif event.state == 1:
		if event.num == 4:
			font1 = (font1[0], font1[1] + 1)
		else:
			font1 = (font1[0], font1[1] - 1)
	elif event.state == 4:
		if event.num == 4:
			subs_bottom_padding += 5
		else:
			subs_bottom_padding -= 5

	# for live resize/reposition
	beysc()
	render_subtitles()

def wheel_click(event):
	global auto_pause
	if auto_pause == 2:
		auto_pause = 0
	else:
		auto_pause += 1

	os.system('echo \'{ "command": ["show-text", "auto_pause: ' + str(auto_pause) + '"] }\' | socat - "' + mpv_socket + '" > /dev/null')

def listen(word):
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

	os.system('(cd /tmp; wget ' + mp3 + '; mpv --loop=1 --volume=40 --force-window=no ' + mp3.split('/')[-1] + '; rm ' + mp3.split('/')[-1] + ') &')

def mpv_pause(e = None):
	if pause_during_translation:
		os.system('echo \'{ "command": ["set_property", "pause", true] }\' | socat - "' + mpv_socket + '" > /dev/null')

def mpv_resume(e = None):
	if pause_during_translation:
		os.system('echo \'{ "command": ["set_property", "pause", false] }\' | socat - "' + mpv_socket + '" > /dev/null')

def mpv_pause_status():
	stdoutdata = subprocess.getoutput('echo \'{ "command": ["get_property", "pause"] }\' | socat - "' + mpv_socket + '"')
	return loads(stdoutdata)['data']

def mpv_fullscreen_status():
	stdoutdata = subprocess.getoutput('echo \'{ "command": ["get_property", "fullscreen"] }\' | socat - "' + mpv_socket + '"')
	return loads(stdoutdata)['data']

# render beyond the screen
def beysc():
	window.geometry('+%d+%d' % (ws+999, hs+999))
	window.update_idletasks()

def stripsd(word):
	return ''.join(e for e in word.strip().lower() if e.isalnum() and not e.isdigit())

#########################################

print('[py part] Starting interSubs ...')
pth = os.path.expanduser('~/.config/mpv/scripts/')
os.chdir(pth)
exec(open('interSubs.conf.py').read())

mpv_socket = sys.argv[1]
sub_file = sys.argv[2]

pons_combos = ['enes', 'enfr', 'deen', 'enpl', 'ensl', 'defr', 'dees', 'deru', 'depl', 'desl', 'deit', 'dept', 'detr', 'deel', 'dela', 'espl', 'frpl', 'itpl', 'plru', 'essl', 'frsl', 'itsl', 'enit', 'enpt', 'enru', 'espt', 'esfr', 'delb', 'dezh', 'enzh', 'eszh', 'frzh', 'denl', 'arde', 'aren', 'dade', 'csde', 'dehu', 'deno', 'desv', 'dede', 'dedx']

if save_translations:
	try:
		os.mkdir('urls')
	except:
		pass

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
c3 = 0
while 1:
	sleep(update_time)
	window.update()

	# hide subs when mpv isn't in focus or in fullscreen
	if inc * update_time > focus_checking_time:
		try:
			if 'mpv' not in subprocess.check_output(['xdotool', 'getwindowfocus', 'getwindowname']).decode("utf8", "ignore") or (hide_when_not_fullscreen and not mpv_fullscreen_status()):
				was_hidden = 1
				beysc()
				frame.destroy()
				popup.destroy()
				continue
		except:
			continue
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

	while tmp_file_subs != subs:
		if auto_pause == 2:
			if not c3 and len(subs.replace('\n', ' ').split(' ')) > auto_pause_min_words - 1 and not mpv_pause_status():
				mpv_pause()
				c3 = 1

			if c3 and mpv_pause_status():
				break

			c3 = 0

		subs = tmp_file_subs
		beysc()
		render_subtitles()

		if auto_pause == 1:
			if len(subs.replace('\n', ' ').split(' ')) > auto_pause_min_words - 1:
				mpv_pause()

		break
