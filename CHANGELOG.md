Changelog
-----
* 2.0a
	* Configs are incompatible with previous version.
	* Tk is abandoned in favor of Qt.
		* Background can be fully transparent or semi/fully opaque.
		* Rendering is faster than with Tk.
		* requires pyqt5 for python 3
			* `pip install pyqt5` / `pacman -S python-pyqt5`
		* requires composite manager for not solid bg; `xcompmgr` or sth.
		* tested on Openbox, i3, KDE(kwin).
		* On KDE(kwin) go to composite and uncheck "Allow applications to block compositing". [screenshot](https://iwf1.com/wordpress/wp-content/uploads/2017/09/Disable-applications-override-compositor-KDE.jpg)
	* No more stalling when pointing on a wrong word; those words will be translated and saved in background.
	* R2L isn't ready yet.
	* Option to not save translations on the disk was removed.
	* Noun colorization was removed.
	* Randomization of translations was removed.
	* Option to show N of previous subtitles is suspended for now, I might add it in the future.
	* Tk version won't be updated unless something critical happens.
* 2.1
	* R2L support (checked on Hebrew; works more or less).
	* Minor corrections.
* 2.2
	* Added https://dict.leo.org/ - de<>en/es/fr/it/pl/pt/ru/zh(cn)
	* Minor corrections.

* 2.3
	* Added option to limit extension of subtitles during long scenes without talking.
		* `extend_subs_duration_limit_sec = 15`
	* Updated https://translate.google.com/
		* Now it gives complete output instead of single result.
		* `mtranslate_google` -> `google`
	* Added http://www.morfix.co.il/
		* `morfix`
	* Minor error corrections.
* 2.4
	* Fixed non-working deepl.com
	* Minor corrections.
* 2.5
	* Added option to hide/show interSubs without exiting - F6
	* Minor corrections.
* 2.6
	* Fixed inability to start after update to pyqt5 5.11.3 or sth in that area. Didn't look for version that causes it specifically.
* 2.7
	* Fixed residual flickering of previous lines during subtitles change. Began to happen at qt5.12 or so.
* 2.8
	* Fixed gtts/pons pronunciation.
	* Fixed google-translation.
* 2.9
	* Added google-translation for full sentences(default mouse Back-click):
		* `f_translation_full_sentence` to bind to mouse instead of `f_deepl_translation`
		* in config `translation_function_name_full_sentence = 'google'`
* 2.10
	* Fixed google-translation
