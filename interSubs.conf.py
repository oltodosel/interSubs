# v. 1.14
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

external_dictionary_cmd_on_click = 'chromium "http://www.linguee.com/german-english/search?source=german&query=${word}"'	# firefox "https://en.wiktionary.org/wiki/${word}"

font1 = ("Trebuchet MS", 34)		# subtitles (font, size)
font2 = ("Trebuchet MS", 28)		# [popup] original language & translation
font3 = ("Trebuchet MS", 24)		# [popup] morphology
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

translation_function_names = ['pons', 'dict_cc']	# dictionaries to use, one or more.
									# or other function's name you might write that will return ([[word, translation]..], [morphology = '', gender = ''])
									# available: pons, reverso, dict_cc, mtranslate_google (one word translation - for uncommon languages)

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

listen_via = 'forvo'					# gtts|pons|forvo # gtts is google-text-to-speech
