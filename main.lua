local PLUGIN_TOGGLE_KEYBIND = "F5"
local VISIBILITY_TOGGLE_KEYBIND = "F6"
local IS_AUTO_START_ON = false
-- for Mac change python3 to python or pythonw
local PYTHON_COMMAND = 'python3 "%s" "%s" "%s"'
local PYTHON_SCRIPT_FILENAME = "interSubs.py"

local python_script_file_path = mp.get_script_directory().."/"..PYTHON_SCRIPT_FILENAME
local random_number = math.random(11111111, 99999999)

local function put_cmd_in_bg(cmd) return cmd.." &" end

local function is_there_no_selected_subs()
	return mp.get_property("sub") == "no" or mp.get_property("sub") == "auto"
end	

local function create_mpv_socket_file()
	-- recomend to have it in tmpfs
	mpv_socket_file_path = "/tmp/mpv_socket"..'_'..random_number
	mp.set_property("input-ipc-server", mpv_socket_file_path)
end

local function destroy_mpv_socket_file()
	mp.set_property("input-ipc-server", "")
	os.execute(put_cmd_in_bg("rm "..mpv_socket_file_path))
end

local function write_sub_to_file(name, value)
	if type(value) == "string" then
		file = io.open(subs_file_path, "w")
		file:write(value)
		file:close()
	end
end

local function create_subs_file()
	-- recomend to have it in tmpfs
	subs_file_path = "/tmp/mpv_sub"..'_'..random_number
	mp.observe_property("sub-text", "string", write_sub_to_file)
end

local function destroy_subs_file()
	mp.unobserve_property(write_sub_to_file)
	os.execute(put_cmd_in_bg("rm "..subs_file_path))
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

local function stop_intersub()
	mp.command('show-text "Quitting interSubs..."')

	os.execute(put_cmd_in_bg("pkill -f "..mpv_socket_file_path))
	destroy_mpv_socket_file()
	destroy_subs_file()
	restore_subs_settings()

	mp.unregister_event(stop_intersub)
	is_running = false
end

local function start_intersub()
	if is_there_no_selected_subs() then
		mp.command('show-text "Select subtitles before starting interSubs."')
		return 
	end
	mp.command('show-text "Starting interSubs..."')

	save_current_subs_settings()
	mp.set_property("sub-visibility", "yes")
	-- TODO: check if it needs to be like this
	mp.set_property("sub-ass-override", "force")
	hide_native_subs()

	create_subs_file()
	create_mpv_socket_file()

	os.execute(put_cmd_in_bg(PYTHON_COMMAND:format(python_script_file_path, mpv_socket_file_path, subs_file_path)))
	mp.register_event("shutdown", stop_intersub)
	is_running = true
end

local function toggle_subs_visibility()
	if not is_running then return end
	if is_visible then
		os.execute(put_cmd_in_bg('touch "'..mpv_socket_file_path..'_hide"'))
		mp.osd_message("Hiding interSubs.", .8)
		is_visible = false
	else
		os.execute(put_cmd_in_bg('rm "'..mpv_socket_file_path..'_hide"'))
		mp.osd_message("Showing interSubs.", .8)
		is_visible = true
	end
end

local function run()
	if is_running then
		stop_intersub()
	else
		start_intersub()
	end
end

local function on_file_loaded()
	if is_there_no_selected_subs() then return end
	if IS_AUTO_START_ON then
		run()
	end
end

mp.add_forced_key_binding(PLUGIN_TOGGLE_KEYBIND, "start-stop-interSubs", run)
mp.add_forced_key_binding(VISIBILITY_TOGGLE_KEYBIND, "hide-show-interSubs", toggle_subs_visibility)
mp.register_event("file-loaded", on_file_loaded)
