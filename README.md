interSubs
=========

Interactive subtitles for [mpv](https://github.com/mpv-player/mpv), that was made to help study languages.  
Easily tweaked and customizable.

v. 2.8 - Changelog at the bottom.  
If Qt version doesn't work for you - use [Tk](https://github.com/oltodosel/interSubs/tree/master/Tk). It is abandoned, but still works.

![z 00_00_5 75-00_00_19 96](https://user-images.githubusercontent.com/10230453/38359595-7f56acc0-38d1-11e8-9a65-257466a44e08.gif)

* Supported dictionaries:
	* https://dict.cc/
	* https://pons.com/
	* http://reverso.net/
	* https://dict.leo.org/
	* https://translate.google.com/
	* http://morfix.co.il/
	* https://redensarten-index.de/
* Offline \t separated dictionary. [pyglossary](https://github.com/ilius/pyglossary)
* https://www.deepl.com/translator for whole sentences.
* http://linguee.com/ redirecting to browser by click.
* https://forvo.com/, https://pons.com/ or Google for pronouncing single words.
* Can use multiple dictionaries simultaneously.
* Reassigning mouse buttons functions in config.
* Doesn't work with DVD (picture based) subtitles, only the text-based ones.
	* [Script](https://github.com/oltodosel/extract_n_convert_dvd_bd_subtitles) to convert picture based subtitles into *.srt; also extracts them from *.mkv 
* Can extend time of subs showing; for slow readers
```
    00:02:23,046 --> 00:02:25,990
    bla bla
    00:02:28,020 --> 00:02:33,084
    waka waka
    
    00:02:23,046 --> 00:02:28,020
    bla bla
    00:02:28,020 --> 00:02:33,084
    waka waka
```

Requirements
------------
   * mpv 0.27 (I don't know if it will work with mpv front-ends.)
   * python => 3.6
   * pyqt5 (pip/pacman/etc)
   * composite manager; xcompmgr or sth.
   * numpy (pip/pacman/etc)
   * beautifulsoup4 (pip/pacman/etc)
   * requests (pip/pacman/etc)
   * python-lxml
   * lua
   * socat
   * pkill
   * xdotool (for hiding subtitles when minimizing mpv or switching window) 
   * optional: chromium (for external translation, other browser can be specified)
   * optional: wget (for listening to pronunciation)

Installation
------------
* `mv interSubs.py interSubs.lua interSubs_config.py ~/.config/mpv/scripts/;`
* Edit configuration file interSubs_config.py
* Edit interSubs.lua to add option where interSubs will start automatically. 
* For Mac also edit configuration at interSubs.lua
* On KDE(kwin) go to composite and uncheck "Allow applications to block compositing". [Screenshot](https://iwf1.com/wordpress/wp-content/uploads/2017/09/Disable-applications-override-compositor-KDE.jpg).
* For Windows - port it yourself.

Usage
-----
* Start video with mpv & select subtitles.
* F5 to start/stop interSubs.
	* Starts automatically with files/paths specified in interSubs.lua
* Point cursor over the word to get popup with translation.
* F6 to hide/show without exiting.

Buttons bellow may be reassigned in config
-----
* Click on the word to look it up on another translator in the browser.
* Right-click on the word to hear its pronunciation.
* Wheel - scroll through transitions in popup.
* Wheel+Ctrl - resize subtitles.
* Wheel+Shift - change subtitles' vertical position.
* Wheel-click - cycle through auto_pause options.
* Wheel-click-left/right - +/- auto_pause_min_words. (fancy mouses)
* Back-click - translate whole sentence. (fancy mouses)

Important
-----
* May have issues working in a multi-monitor system.  See [the solution](https://github.com/oltodosel/interSubs/issues/26).
* On KDE subtitles might sometimes be invisible. See [the solution](https://github.com/oltodosel/interSubs/issues/12#issuecomment-433960146).
* Instead of changing system settings you may change [--x11-bypass-compositor](https://mpv.io/manual/stable/#options-x11-bypass-compositor)
* Stuttering video during subtitles change might be solved by changing mpv's video output `mpv --vo gpu`.

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
	
