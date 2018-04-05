interSubs
=========

v. 1.23 - Changelog at the bottom.

Interactive subtitles for `mpv`, that was made to help study languages. Easily tweaked and customizable.

- https://dict.cc/, https://pons.com/, http://reverso.net/, https://redensarten-index.de/ or Google for single words
- Offline \t separated dictionary. (https://github.com/ilius/pyglossary)
- https://www.deepl.com/translator for whole sentences.
- http://linguee.com/ redirecting to browser by click.
- https://forvo.com/, https://pons.com/ or Google for pronouncing single words.
- Can use multiple dictionaries simultaneously. 
-
- Doesn't work with DVD (picture based) subtitles, only the text-based ones.
- To convert picture based subtitles into *.srt; also extracts them from *.mkv [extract_n_convert_dvd_bd_subtitles](https://github.com/oltodosel/extract_n_convert_dvd_bd_subtitles)
-
- Can colorize nouns by gender; German only with given dictionary.
- Works with right-to-left writing.
- Autodetects Hebrew and switches to r2l.
- Reassigning buttons' functions in config.
- Can extend time of subs showing; for slow readers

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

![ezgif com-video-to-gif](https://cloud.githubusercontent.com/assets/10230453/22852882/683b508e-f04f-11e6-87d0-7477164a1709.gif)

Requirements
------------
   - mpv 0.27 (I don't know if it will work with mpv front-ends.)
   - python 3
   - numpy (pip)
   - beautifulsoup4 (pip)
   - mttkinter (pip) (works without it, but slower)
   - Tcl/Tk 8.6.6
   - lua
   - socat
   - pkill
   - xdotool (for hiding subtitles when minimizing mpv or switching window) 
   - optional: chromium (for external translation, other browser can be specified)
   - optional: wget (for listening to pronunciation)

Installation
------------
```
mv interSubs.py interSubs.lua interSubs.conf.py ~/.config/mpv/scripts/;
mv interSubs.delexicon.txt ~/.config/mpv/scripts/; # only for German nouns colorization
# Edit configuration file interSubs.conf.py
# For Mac also edit configuration at interSubs.lua
# For Windows - port it yourself.
```

Usage
-----
- Start video with mpv & select subtitles.
- Press F5 to start/stop interSubs.
- Point cursor over the word to get popup with translation.

Buttons bellow may be reassigned in config
-----
- Click on the word to look it up on another translator in the browser.
- Right-click on the word to hear its pronunciation.
- Wheel - scroll through transitions in popup.
- Wheel+Ctrl - resize subtitles.
- Wheel+Shift - change subtitles' vertical position.
- Wheel-click - cycle through auto_pause options.
- Wheel-click-left/right - +/- auto_pause_min_words. (fancy mouses)
- Back-click - translate whole sentence. (fancy mouses)

Important
-----
- By default works only in fullscreen.
- May have issues working in a multi-monitor system.

Changelog
-----
* 1.14 - Added simultaneous use of multiple dictionaries. When using more than one - scrolling is infinite.
* 1.15 - Added multi-threaded retrieval when using more than one dictionary. Works only with `save_translations = 1`
* 1.16 - Added waiting cursor. Minor errors correction.
* 1.17 - Minor errors correction.
* 1.18 - Added redensarten-index.de support (German idioms).
* 1.19
    * Added option to reassign buttons.
    * Added support for deepl.com; to translate whole sentences.
        * Supported languages: de, en, fr, es, it, nl, pl.
    * Version are not back compatible with previous config.
* 1.20 - Added function to save words to a file. Boundable to a mouse-button.
* 1.21 - Minor error correction.
* 1.22 - Added \t separated offline dictionary support.
* 1.23
    * Added support for subtitles with more than 2 lines.
    * Added support for subtitles to be at the top of the screen.
        * `subs_top_placement_B = True`
    * Added simultaneous creation of buttons for words using [mtTkinter](https://github.com/RedFantom/mtTkinter).
        * Speeds up rendering 2-5x, especially noticeable on long sentences.
        * `pip install mttkinter`
    * Added option to show N of previous subtitles.
        * Might be slow without mtTkinter, especially when having script show too many previous lines.
        * `show_N_of_previous_subtitles = N`
		
