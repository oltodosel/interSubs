interSubs
=========

Interactive subtitles for [mpv](https://github.com/mpv-player/mpv), that was made to help study languages.  
Easily tweaked and customizable.

![z 00_00_5 75-00_00_19 96](https://user-images.githubusercontent.com/10230453/38359595-7f56acc0-38d1-11e8-9a65-257466a44e08.gif)

* Supported dictionaries for words:
	* https://dict.cc/
	* https://pons.com/
	* http://reverso.net/
	* https://dict.leo.org/
	* https://translate.google.com/
	* http://morfix.co.il/
	* https://redensarten-index.de/
* Supported dictionaries for sentences:
	* https://www.deepl.com/translator
	* https://translate.google.com/
* Supported dictionaries for word pronunciation:
	* https://forvo.com/
	* https://pons.com/
	* https://translate.google.com/
* Offline \t separated dictionary. [details](https://github.com/oltodosel/interSubs/issues/36#issuecomment-803541985) | [pyglossary](https://github.com/ilius/pyglossary)
* http://linguee.com/ redirecting to browser by click.
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
   * Xorg (ignore for Mac users)
   * composite manager; `xcompmgr` or sth. (ignore for Mac users)
   * python => 3.6
   * python-pyqt5
   * python-numpy
   * python-beautifulsoup4
   * python-requests
   * python-lxml
   * python-httpx
   * lua
   * socat
   * pkill
   * xdotool (for hiding subtitles when minimizing mpv or switching window) 
   * optional: chromium (for external translation, other browser can be specified)
   * optional: wget (for listening to pronunciation)

Installation
------------
* `mv interSubs.py interSubs_config.py ~/.config/mpv/scripts/; mv main.lua ~/.config/mpv/scripts/interSubs.lua`
  * or `cd ~/.config/mpv/scripts/; git clone "this repository link"`
* Edit configuration file `interSubs_config.py`
* Edit the lua file if you want change keybindings and should the plugin auto-start or not. 
* For Mac also edit configuration at `interSubs.lua`
* On KDE(kwin) go to Compositor and uncheck "Allow applications to block compositing". [Screenshot](https://iwf1.com/wordpress/wp-content/uploads/2017/09/Disable-applications-override-compositor-KDE.jpg).
* For Windows - port it yourself. (It does NOT work on Windows. [reason](https://github.com/mpv-player/mpv/blob/master/DOCS/man/ipc.rst#command-prompt-example)) and [a possible way to do it](https://github.com/oltodosel/interSubs/issues/40#issuecomment-835767040)). Consider installing VirtualBox and Ubuntu or some other user-friendly distro.

Usage
-----
* Start video with mpv & select subtitles.
* F5 to start/stop interSubs.
* Point cursor over the word to get popup with translation.
* F6 to hide/show without exiting.

Buttons bellow may be reassigned in config
-----
* Left-click - show translation in your browser.
* Right-click - listen to pronunciation.
* Wheel - scroll through transitions in popup.
* Wheel+Ctrl - resize subtitles.
* Wheel+Shift - change subtitles' vertical position.
* Wheel-click - cycle through auto_pause options.
* Wheel-click-left/right - +/- auto_pause_min_words. (fancy mouses)
* Back-click - translate whole sentence. (fancy mouses)

Troubleshooting
-----
* Does not work at all - launch `mpv` in a console, then start `interSubs` and see if there are any errors that might indicate on missing packages and install them.
* Background and subtitles are shown as solid black bars - install/launch a compositor.
* May have issues working in a multi-monitor system.  See [the solution](https://github.com/oltodosel/interSubs/issues/26).
* On KDE subtitles might sometimes be invisible. See [the solution](https://github.com/oltodosel/interSubs/issues/12#issuecomment-433960146).
* On KDE subtitles fade instead of appearing immediately. See [the solution](https://github.com/oltodosel/interSubs/issues/39#issuecomment-810483614)
* Instead of changing system settings you may change [--x11-bypass-compositor](https://mpv.io/manual/stable/#options-x11-bypass-compositor)
* Stuttering video during subtitles change might be solved by changing mpv's video output `mpv --vo gpu`.
* On MacOS subtitles are not rendered on top of `mpv`. See [a possible solution](https://github.com/oltodosel/interSubs/issues/42#issuecomment-841725012)
* On MacOS subtitles are not rendered on top of `mpv` only in fullscreen mode. See [the solution](https://github.com/oltodosel/interSubs/issues/42#issuecomment-841746404)

[Changelog](CHANGELOG.md)
-----