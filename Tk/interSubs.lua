-- v. 1.22
-- Interactive subtitles for `mpv` for language learners.
--
-- default keybinding: F5
-- if interSubs start automatically - mpv won't show notification
--
-- dirs in which interSubs will start automatically; part of path/filename will also work; case insensitive; regexp
autostart_in = {'/med/doc', 'German', ' ger ', '%.ger%.', 'Deutsch', 'Hebrew'}
-- for Mac change python3 to python or pythonw
start_command = 'python3 "%s" "%s" "%s"'

sub_file = '/tmp/mpv_sub'
mpv_socket = '/tmp/mpv_socket'
pyname = '~/.config/mpv/scripts/interSubs.py'

function s1()
	if running == true then
		s_rm()
		return
	end

	running = true
	mp.msg.warn('Starting interSubs ...')
	mp.register_event("end-file", s_rm)

	rnbr = math.random(11111,99999)
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
	mp.msg.warn('Quitting interSubs ...')

	mp.set_property("sub-visibility", sbv)
	mp.set_property("sub-color", sub_color1)
	mp.set_property("sub-border-color", sub_color2)
	mp.set_property("sub-shadow-color", sub_color3)

	os.execute('pkill -f "' .. mpv_socket_2 .. '"')
	os.execute('(sleep 3 && rm "' .. mpv_socket_2 .. '") &')
	os.execute('(sleep 3 && rm "' .. sub_file_2 .. '") &')
end

function started()
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
		mp.command('show-text "Quitting interSubs ..."')
	else
		s1()
		mp.command('show-text "Starting interSubs ..."')
	end
end

mp.add_forced_key_binding("f5", "start-stop-interSubs", s1_1)
mp.register_event("start-file", started)
