-- default keybinding: F5
-- dir in which interSubs will start automatically
autostart_in = "/med/p/TV/"
--

sub_file = "/tmp/mpv_sub"
pyname = '~/.config/mpv/scripts/interSubs.py'

function s1()
	if running == true then
        s_rm()
        return
    end
	running = true
    mp.command('show-text "Starting interSubs ..."')
    mp.msg.warn('Starting interSubs ...')

    -- setting up socket to control mpv
    mp.set_property("input-ipc-server", '/tmp/mpv_socket')

    -- without visible subs won't work
    sfs1 = mp.get_property_number("sub-font-size")
    sfs2 = mp.get_property_number("sub-scale")
    mp.set_property("sub-visibility", "yes")
    mp.set_property_number("sub-font-size", 1)
    mp.set_property_number("sub-scale", 0.01)

    os.execute('python3 ' .. pyname:gsub("~", os.getenv("HOME")) .. ' &')

    mp.observe_property("sub-text", "string", s2)
    mp.register_event("end-file", s_rm)
    mp.register_event("quit", s_rm)
end

function s2()
    st = mp.get_property("sub-text")

    file = io.open(sub_file, "w")
    if type(st) == "string" then file:write(st) end
    file:close()
end

function s_rm()
    running = false

    mp.set_property_number("sub-font-size", sfs1)
    mp.set_property_number("sub-scale", sfs2)
	
    mp.command('show-text "Quitting interSubs ..."')
    mp.msg.warn('Quitting interSubs ...')
    os.remove(sub_file)
    os.execute('pkill -f "python3 ' .. pyname:gsub("~", os.getenv("HOME")) .. '"')
end

function started()
    if mp.get_property("path"):find('^' .. autostart_in) ~= nil then
        s1()
    end
end

mp.add_forced_key_binding("f5", "111", s1)
mp.register_event("start-file", started)
