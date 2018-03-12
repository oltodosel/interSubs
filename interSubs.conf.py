# v. 1.23
# Interactive subtitles for `mpv` for language learners.

# BEWARE!
# treat this config like python
# next line shows how the main scripts gets these variables
# exec(open('interSubs.conf.py').read())

#########################################

# make sure selected translation function supports your language and so that codes of your languages are correct
# for instance Pons doesn't support Hebrew, Google and Reverso do, but their codes are different: 'iw' and 'he' respectively
# translate from language
lang_from = 'de'
# translate to language
lang_to = 'en'

############
# all *_B variables are boolean
############

pause_during_translation_B = True
# don't hide subtitle when its time is up and keep it on screen until the next line
extend_subs_duration2max_B = True
# show interSubs only in fullscreen
hide_when_not_fullscreen_B = True
# saving to ~/.config/mpv/scripts/urls/
save_translations_B = True
# every translation but first will be shuffled # scrolling through transitions would be disabled
randomize_translations_B = False

############################################

# translated language is written right-to-left, e.g Hebrew/Arabic
R2L_from_B = False
# translation is written right-to-left, e.g Hebrew/Arabic
R2L_to_B = False

font1 = ("Trebuchet MS", 33)		# subtitles (font, size)
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

# show subtitles at the top of the screen
subs_top_placement_B = False
subs_screen_edge_padding = 5
popup_ext_n_int_padding = 5

##################################################

# number of translations in popup
number_of_translations = 3
# number of translations to save in files for each word; 0 - to save all
number_of_translations_to_save = 0

# interval in seconds between checking for the next subtitle
update_time = .01
# interval in seconds between checking if mpv is in focus using `xdotool` and/or in fullscreen
focus_checking_time = .1

# firefox "https://en.wiktionary.org/wiki/${word}"
show_in_browser = 'chromium "http://www.linguee.com/german-english/search?source=german&query=${word}"'

# dictionaries to use, one or more
# or other function's name you might write that will return ([[word, translation]..], [morphology = '', gender = ''])
# available:
#	pons
#	reverso
#	dict_cc
#	mtranslate_google (one word translation - for uncommon languages)
#	redensarten (redensarten-index.de - German idioms etc.)
#	tab_divided_dict - offline dictionary with word \t translation
translation_function_names = ['dict_cc', 'pons']

# path to the offline dictionary
tab_divided_dict_fname = '~/d/python_shit/mpv/scripts/z'
# strip <.*?>
tab_divided_dict_remove_tags_B = True

# for going through lines step by step
# skip pausing when subs are less then X words
auto_pause_min_words = 10
# 0 - don't pause
# 1 - pause after subs change
# 2 - pause before subs change
# wheel click on interSubs cycles through options
auto_pause = 0

# when subtitle consists of only one overly long line - splitting into two
split_long_lines_B = True
# split when there are more than N words in line
split_long_lines_words_min = 7
# colorize nouns by gender; German only with given dictionary
colorize_nouns_B = False

# it should have pattern: Word\t\tGender\t...
# exact genders are Masc/Fem/Neut
colorization_dict = 'interSubs.delexicon.txt'

# gtts|pons|forvo # gtts is google-text-to-speech
listen_via = 'gtts'

# filename where to save words if needed by bound to mouse-button function f_save_word_to_file; checks if the word is already there.
save_word_to_file_fname = '~/saved_words_by_interSubs'

# number of previous subtitles to show [0..inf]
show_N_of_previous_subtitles = 0
# show prev. subs above or below current; active if show_N_of_previous_subtitles > 0
show_previous_subtitles_above_current_B = True

###################################################
###################################################
# reassigning mouse buttons #
###################################################
###################################################
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
	# f_subs_screen_edge_padding_decrease
	# f_subs_screen_edge_padding_increase
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

	[4, 1, 'f_subs_screen_edge_padding_decrease'],
	[5, 1, 'f_subs_screen_edge_padding_increase'],

	[4, 4, 'f_font_size_decrease'],
	[5, 4, 'f_font_size_increase'],

	[6, 0, 'f_auto_pause_min_words_decrease'],
	[7, 0, 'f_auto_pause_min_words_increase'],
	[8, 0, 'f_deepl_translation'],

	[9, 0, ''],
]


################################
# below backwards compatibility stuff
################################
pause_during_translation = pause_during_translation_B
extend_subs_duration2max = extend_subs_duration2max_B
hide_when_not_fullscreen = hide_when_not_fullscreen_B
save_translations = save_translations_B
randomize_translations = randomize_translations_B
R2L_from = R2L_from_B
R2L_to = R2L_to_B
tab_divided_dict_remove_tags = tab_divided_dict_remove_tags_B
split_long_lines = split_long_lines_B
colorize_nouns = colorize_nouns_B
subs_bottom_padding = subs_screen_edge_padding
