-- v. 2.7
-- Interactive subtitles for `mpv` for language learners.
--
-- default keybinding to start/stop: F5
-- default keybinding to hide/show: F6
-- if interSubs start automatically - mpv won't show notification
--
-- dirs in which interSubs will start automatically; part of path/filename will also work; case insensitive; regexp
-- autostart_in = {'German', ' ger ', '%.ger%.', 'Deutsch', 'Hebrew'}
autostart_in = {'Hebrew'}

-- for Mac change python3 to python or pythonw
start_command = 'python3 "%s" "%s" "%s"'

-- recomend to have these in tmpfs, or at least ssd.
sub_file = '/tmp/mpv_sub'
mpv_socket = '/tmp/mpv_socket'

keybinding = 'F5'
keybinding_hide = 'F6'

pyname = '~/.config/mpv/scripts/interSubs.py'

------------------------------------------------------

debug = false
-- debug = true

if debug == true then
	start_command = ''
	start_command = 'terminator -e \'python3 "%s" "%s" "%s"; sleep 33\''
end

------------------------------------------------------

function s1()
	if running == true then
		s_rm()
		return
	end

	running = true
	mp.msg.warn('Starting interSubs ...')
	mp.register_event("end-file", s_rm)
	rnbr = math.random(11111111, 99999999)

	if debug == true then
		rnbr = ''
	end

	mpv_socket_2 = mpv_socket .. '_' .. rnbr
	sub_file_2 =  sub_file .. '_' .. rnbr
	
	-- setting up socket to control mpv
	mp.set_property("input-ipc-server", mpv_socket_2)
	
	-- without visible subs won't work
	sbv = mp.get_property("sub-visibility")
	mp.set_property("sub-visibility", "yes")
	mp.set_property("sub-ass-override", "force")
	
	sub_color1 = mp.get_property("sub-color", "1/1/1/1")
	sub_color2 = mp.get_property("sub-border-color", "0/0/0/1")
	sub_color3 = mp.get_property("sub-shadow-color", "0/0/0/1")
	mp.set_property("sub-color", "0/0/0/0")
	mp.set_property("sub-border-color", "0/0/0/0")
	mp.set_property("sub-shadow-color", "0/0/0/0")

	start_command_2 = start_command:format(pyname:gsub('~', os.getenv('HOME')), mpv_socket_2, sub_file_2)
	os.execute(start_command_2 .. ' &')

	mp.observe_property("sub-text", "string", s2)
end

function s2(name, value)
	if type(value) == "string" then
		file = io.open(sub_file_2, "w")
		file:write(value)
		file:close()
	end
end

function s_rm()
	running = false
	hidden = false
	mp.msg.warn('Quitting interSubs ...')

	mp.set_property("sub-visibility", sbv)
	mp.set_property("sub-color", sub_color1)
	mp.set_property("sub-border-color", sub_color2)
	--~ mp.set_property("sub-shadow-color", sub_color3)

	os.execute('pkill -f "' .. mpv_socket_2 .. '" &')
	os.execute('(sleep 3 && rm "' .. mpv_socket_2 .. '") &')
	os.execute('(sleep 3 && rm "' .. sub_file_2 .. '") &')
end

function started()
	if mp.get_property("sub") == 'no' then
		return true
	end
	
	hidden = false

	for kk, pp in pairs(autostart_in) do
		if mp.get_property("path"):lower():find(pp:lower()) or mp.get_property("working-directory"):lower():find(pp:lower()) then
			s1()
			break
		end
	end
end

function s1_1()
	if running == true then
		s_rm()
		mp.command('show-text "Quitting interSubs..."')
	else
		if mp.get_property("sub") == 'no' then
			mp.command('show-text "Select subtitles before starting interSubs."')
		else
			s1()
			mp.command('show-text "Starting interSubs..."')
		end
	end
end

function hide_show()
	if running == true then
		if hidden == true then
			os.execute('rm "' .. mpv_socket_2 .. '_hide" &')
			mp.osd_message("Showing interSubs.", .8)
			hidden = false
		else
			os.execute('touch "' .. mpv_socket_2 .. '_hide" &')
			mp.osd_message("Hiding interSubs.", .8)
			hidden = true
		end
	end
end

mp.add_forced_key_binding(keybinding, "start-stop-interSubs", s1_1)
mp.add_forced_key_binding(keybinding_hide, "hide-show-interSubs", hide_show)
mp.register_event("file-loaded", started)
