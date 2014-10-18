-- One Platform Lua script that gets client information
--

-- alias[''] references the client
local dev_name = alias[''].name 
debug(string.format('Device Name: %s',dev_name))

local meta_string = alias[''].meta -- get the device client's meta
local meta = json.decode(meta_string) -- decode the json string into Lua table
-- Portals puts this application specific stuff into meta as a JSON string
local dev_tz = meta.timezone
local dev_location = meta.location
local dev_acttime = meta.activetime
local dev_type = meta.device.type

debug('print information found in meta')

debug(string.format('Device Timezone: %s',dev_tz))
debug(string.format('Device Loc: %s',dev_location))
debug(string.format('Device Activation Time: %s',dev_acttime))
debug(string.format('Device Device Type: %s',dev_type))

local ret,info = alias[''].manage.info("", {"aliases","basic","counts","description","key","shares","storage","subscribers","tagged","tags","usage"})

if ret then 
	debug(string.format(info))
end

