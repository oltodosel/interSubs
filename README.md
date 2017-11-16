interSubs
=========

v. 1.11

Interactive subtitles for `mpv`, that was made to help study languages. Easily tweaked and customizable.

 - Uses http://pons.com/, http://reverso.net/ or Google for translation and http://linguee.com/ redirecting to browser by click.
- Linguee, unlike Pons, bans excessive usage by IP, so don't overuse it or write scrapping functions for it.
- Pons has an API, but it's limited to 1k requests per month, so scraping it is.
-
- Doesn't work with DVD (picture based) subtitles, only the text-based ones.
- To convert picture based subtitles into *.srt - https://github.com/oltodosel/extract_n_convert_dvd_bd_subtitles
-
- Can colorize nouns by gender; German only with given dictionary.
- Works with right-to-left writing.
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
   - mpv 0.25 (I don't know if it will work with mpv front-ends.)
   - Python 3
   - numpy (pip)
   - beautifulsoup4 (pip)
   - Tcl/Tk 8.6.6
   - Lua
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
- Click on the word to look it up on another translator in the browser.
- Right-click on the word to hear its pronunciation.
- Wheel - scroll through transitions in popup.
- Wheel+Shift - resize subtitles.
- Wheel+Ctrl - change subtitles' vertical position.
- Wheel-click - cycle through auto_pause options.
- Wheel-click-left/right - +/- auto_pause_min_words. (fancy mouses)
