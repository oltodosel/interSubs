# v. 1.20
# Interactive subtitles for `mpv` for language learners.

# BEWARE!
# treat this config like python
# next line shows how the main scripts gets these variables
# exec(open('interSubs.conf.py').read())

#########################################

# make sure selected translation function supports your language and so that codes of your languages are correct
# for instance Pons doesn't support Hebrew, Google and Reverso do, but their codes are different: 'iw' and 'he' respectively
lang_from = 'de'					# translate from language
lang_to = 'en'						# translate to language

pause_during_translation = 1		# True/False == 1/0
extend_subs_duration2max = 1		# True/False # don't hide subtitle when its time is up and keep it on screen until the next line
hide_when_not_fullscreen = 1		# True/False # show interSubs only in fullscreen

save_translations = 1				# True/False # saving to ~/.config/mpv/scripts/urls/
randomize_translations = 0			# True/False # every translation but first will be shuffled # scrolling through transitions would be disabled

R2L_from = 0						# True/False # translated language is written right-to-left, e.g Hebrew/arabic
R2L_to = 0							# True/False # translation is written right-to-left, e.g Hebrew/arabic

number_of_translations = 3			# number of translations in popup
number_of_translations_to_save = 0	# number of translations to save in files for each word; 0 - to save all

update_time = .01					# interval in seconds between checking for the next subtitle #
focus_checking_time = .1			# interval in seconds between checking if mpv is in focus using `xdotool` and/or in fullscreen

font1 = ("Trebuchet MS", 32)		# subtitles (font, size)
font2 = ("Trebuchet MS", 27)		# [popup] original language & translation
font3 = ("Trebuchet MS", 23)		# [popup] morphology
font_color1 = '#BAC4D6'				# subtitles
font_color2 = '#DCDCCC'				# [popup] original language
font_color3 = '#8B8F88'				# [popup] translation
font_color4 = '#CA8200'				# [popup] morphology
font_color5 = '#1E90FF'				# [popup] nouns, masculine
font_color6 = '#BD3030'				# [popup] nouns, feminine
font_color7 = '#6DB56D'				# [popup] nouns, neuter

font_color8 = '#5EB0FF'				# [colorize_nouns] nouns, masculine
font_color9 = '#FFA6B5'				# [colorize_nouns] nouns, feminine
font_color10 = '#90EE90'			# [colorize_nouns] nouns, neuter

bg_color1 = '#000000'				# subtitles
bg_color2 = '#2C2C2C'				# translation popup

subs_bottom_padding = 5
popup_ext_n_int_padding = 6

show_in_browser = 'chromium "http://www.linguee.com/german-english/search?source=german&query=${word}"'	# firefox "https://en.wiktionary.org/wiki/${word}"

translation_function_names = ['pons', 'dict_cc', 'redensarten']	# dictionaries to use, one or more.
									# or other function's name you might write that will return ([[word, translation]..], [morphology = '', gender = ''])
									# available:
									# pons
									# reverso
									# dict_cc
									# mtranslate_google (one word translation - for uncommon languages)
									# redensarten (redensarten-index.de - German idioms etc.)

# for going through lines step by step
auto_pause_min_words = 10			# skip pausing when subs are less then X words
auto_pause = 0						# 0 - don't pause
									# 1 - pause after subs change
									# 2 - pause before subs change
									# wheel click on interSubs cycles through options

split_long_lines = 1				# when subtitle consists of only one overly long line - splitting into two
split_long_lines_words_min = 7		# split when there are more than N words in line

colorize_nouns = 0 					# colorize nouns by gender; German only with given dictionary

# it should have pattern: Word\t\tGender\t...
# exact genders are Masc/Fem/Neut
colorization_dict = 'interSubs.delexicon.txt'

listen_via = 'gtts'					# gtts|pons|forvo # gtts is google-text-to-speech

translate_whole_sentences = 1		# translate whole sentences with deepl.com
									# mouse-button = 8

# filename where to save words if needed by bound to mouse-button function f_save_word_to_file; checks if the word is already there.
save_word_to_file_fname = '~/saved_words_by_interSubs'

# reassigning mouse buttons
# functions' names are self-explanatory
# [mouse_event, modifier_key, 'self_explanatory_function_name']

# to one button multiple functions can be assigned
# by left-click this will open word in browser and save it to file.
# [1, 0, 'f_show_in_browser']
# [1, 0, 'f_save_word_to_file']

# mouse_event:
	# 1 == left-click
	# 2 == middle-click(wheel)
	# 3 == right-click
	# 4 == wheel down
	# 5 == wheel up
	# 6 == [non-standart] wheel left-click
	# 7 == [non-standart] wheel right-click
	# 8 == [non-standart] forward-button
	# 9 == [non-standart] back-button

# modifier_key:
	# 0 == None
	# 1 == Shift
	# 4 == Ctrl

# self_explanatory_function_name:
	# f_show_in_browser
	# f_auto_pause_options
	# f_listen
	# f_scroll_translations_down
	# f_scroll_translations_up
	# f_subs_bottom_padding_decrease
	# f_subs_bottom_padding_increase
	# f_font_size_decrease
	# f_font_size_increase
	# f_auto_pause_min_words_decrease
	# f_auto_pause_min_words_increase
	# f_deepl_translation
	# f_save_word_to_file
	
mouse_buttons = [
	[1, 0, 'f_show_in_browser'],
	[2, 0, 'f_auto_pause_options'],
	[3, 0, 'f_listen'],
	
	[4, 0, 'f_scroll_translations_down'],
	[5, 0, 'f_scroll_translations_up'],
	
	[4, 1, 'f_subs_bottom_padding_decrease'],
	[5, 1, 'f_subs_bottom_padding_increase'],
	
	[4, 4, 'f_font_size_decrease'],
	[5, 4, 'f_font_size_increase'],
	
	[6, 0, 'f_auto_pause_min_words_decrease'],
	[7, 0, 'f_auto_pause_min_words_increase'],
	[8, 0, 'f_deepl_translation'],
	
	[9, 0, ''],
]
