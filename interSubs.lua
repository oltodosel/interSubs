local PLUGIN_TOGGLE_KEYBIND = "F5"
local VISIBILITY_TOGGLE_KEYBIND = "F6"
-- TODO: Probably needs to be changed. See utils.subprocess(t) and mp.command_native or mp.command_native_async
-- for Mac change python3 to python or pythonw
local PYTHON_COMMAND = 'python3 "%s" "%s" "%s"'
local python_script_file = os.getenv("HOME").."/.config/mpv/scripts/interSubs.py"

local random_number = math.random(11111111, 99999999)

local function create_mpv_socket_file()
	-- recomend to have it in tmpfs
	mpv_socket_file = "/tmp/mpv_socket"
	mpv_socket_file = mpv_socket_file .. '_' .. random_number
	mp.set_property("input-ipc-server", mpv_socket_file)
end

local function create_subs_file()
	-- recomend to have it in tmpfs
	subs_file = "/tmp/mpv_sub"
	subs_file =  subs_file .. '_' .. random_number
end

local function save_current_subs_settings()
	sub_visibility = mp.get_property("sub-visibility")
	sub_color = mp.get_property("sub-color", "1/1/1/1")
	sub_border_color = mp.get_property("sub-border-color", "0/0/0/1")
	sub_shadow_color = mp.get_property("sub-shadow-color", "0/0/0/1")
end

local function restore_subs_settings()
	mp.set_property("sub-visibility", sub_visibility)
	mp.set_property("sub-color", sub_color)
	mp.set_property("sub-border-color", sub_border_color)
	-- mp.set_property("sub-shadow-color", sub_shadow_color)
end

local function hide_native_subs()
	mp.set_property("sub-color", "0/0/0/0")
	mp.set_property("sub-border-color", "0/0/0/0")
	mp.set_property("sub-shadow-color", "0/0/0/0")
end

local function write_sub_to_file(name, value)
	if type(value) == "string" then
		file = io.open(subs_file, "w")
		file:write(value)
		file:close()
	end
end

local function release_resources()
	-- TODO: needs refactoring
	os.execute('pkill -f "' .. mpv_socket_file .. '" &')
	os.execute('(sleep 3 && rm "' .. mpv_socket_file .. '") &')
	os.execute('(sleep 3 && rm "' .. subs_file .. '") &')
end

local function start_intersub()
	mp.command('show-text "Starting interSubs..."')
	mp.msg.warn('Starting interSubs ...')

	if mp.get_property("sub") == 'no' then
		mp.command('show-text "Select subtitles before starting interSubs."')
	end

	mp.set_property("sub-visibility", "yes")
	-- TODO: check if it needs to be like this
	mp.set_property("sub-ass-override", "force")

	save_current_subs_settings()
	hide_native_subs()

	create_mpv_socket_file()
	create_subs_file()
	mp.observe_property("sub-text", "string", write_sub_to_file)
	
	os.execute(PYTHON_COMMAND:format(python_script_file, mpv_socket_file, subs_file)..' &')
	mp.register_event("end-file", stop_intersub)
end

local function stop_intersub()
	mp.command('show-text "Quitting interSubs..."')
	mp.msg.warn('Quitting interSubs ...')

	restore_subs_settings()
	mp.unobserve_property(write_sub_to_file)
	release_resources()

	mp.unregister_event(stop_intersub)
end

local function on_file_loaded()
	if mp.get_property("sub") == 'no' then return end
	
	run()
end

local function toggle_subs_visibility()
	-- TODO: doesn't look like it would work properly..., change it
	if is_running then
		if is_visible then
			os.execute('rm "' .. mpv_socket_file .. '_hide" &')
			mp.osd_message("Showing interSubs.", .8)
			is_visible = false
		else
			os.execute('touch "' .. mpv_socket_file .. '_hide" &')
			mp.osd_message("Hiding interSubs.", .8)
			is_visible = true
		end
	end
end

local function run()
	if is_running then
		stop_intersub()
		is_running = false
	else
		start_intersub()
		is_running = true
	end
end

mp.add_forced_key_binding(PLUGIN_TOGGLE_KEYBIND, "start-stop-interSubs", run)
mp.add_forced_key_binding(VISIBILITY_TOGGLE_KEYBIND, "hide-show-interSubs", toggle_subs_visibility)
mp.register_event("file-loaded", on_file_loaded)
