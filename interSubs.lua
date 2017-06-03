-- v. 1.7
-- Interactive subtitles for `mpv` for language learners.

-- default keybinding: F5
-- dirs in which interSubs will start automatically
autostart_in = {'/med/p/TV', '/med/German', '/med/video/youtube', '/med/2see', '/med/p/Movies'}
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

	mp.register_event("end-file", s_rm)
	mp.register_event("quit", s_rm)

	--os.execute('notify-send -i none -t 999 "Starting interSubs ..."')
	--mp.command('show-text "Starting interSubs ..."')
	mp.msg.warn('Starting interSubs ...')

	running = true
	rnbr = math.random(111111,999999)

	-- setting up socket to control mpv
	mpv_socket_2 = mpv_socket .. '_' .. rnbr
	mp.set_property("input-ipc-server", mpv_socket_2)
	sub_file_2 =  sub_file .. '_' .. rnbr

	-- without visible subs won't work
	sfs1 = mp.get_property_number("sub-font-size")
	sfs2 = mp.get_property_number("sub-scale")
	mp.set_property("sub-visibility", "yes")
	mp.set_property_number("sub-font-size", 1)
	mp.set_property_number("sub-scale", 0.01)

	start_command_2 = start_command:format(pyname:gsub('~', os.getenv('HOME')), mpv_socket_2, sub_file_2)
	os.execute(start_command_2 .. ' &')

	mp.observe_property("sub-text", "string", s2)
end

function s2()
	st = mp.get_property("sub-text")

	if type(st) == "string" then
		file = io.open(sub_file_2, "w")
		file:write(st)
		file:close()
	end
end

function s_rm()
	running = false

	mp.set_property_number("sub-font-size", sfs1)
	mp.set_property_number("sub-scale", sfs2)

	--os.execute('notify-send -i none -t 999 "Quitting interSubs ..."')
	--mp.command('show-text "Quitting interSubs ..."')
	mp.msg.warn('Quitting interSubs ...')

	os.execute('pkill -f "' .. mpv_socket_2 .. '"')
	os.remove(sub_file_2)
	os.remove(mpv_socket_2)
end

function started()
	for kk, pp in pairs(autostart_in) do
		if mp.get_property("path"):find(pp) or mp.get_property("working-directory"):find(pp) then
			s1()
		end
	end
end

mp.add_forced_key_binding("f5", "start-stop-interSubs", s1)
mp.register_event("start-file", started)
