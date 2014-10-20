-- One Platform Lua script that gets client information
--

-- alias[''] references the client
local dev_name = alias[''].name 
debug(string.format('Device Name: %s',dev_name))

debug('get device client meta')
local meta_string = alias[''].meta -- get the device client's meta
--debug(string.format('META String: %s',meta_string))

-- Decode the string into a Lua table
local meta = json.decode(meta_string)
-- Portals puts this application specific stuff into meta as a JSON string
local dev_tz = meta.timezone
local dev_location = meta.location
local dev_acttime = meta.activetime
local dev_type = meta.device.type

--debug('print applicaiton specific found in meta put there by the Poratls')
--debug(string.format('Timezone: %s, Location: %s, Active Time Interval: %s, Device Type: %s',dev_tz,dev_location,dev_acttime,dev_type))


debug('get device client information')
local success,info = manage.info(
		{alias = ""}, 
		{"aliases","basic","counts","description","key","shares","storage","subscribers","tagged","tags","usage"})

if not success then 
	debug('could not get device client info')
end

debug('get device client list')
local success,listing = alias[''].manage.listing({"client","dataport","datarule","dispatch"},{"owned",})

if not success then 
	debug('could not get device client listing')
end

-- send a nice email report to yourself for your client information:
local emailaddress = '<YOUREMAILADDRESSHERE>'
local subject = 'My Device Information'
local report = 'Report\n\n'

report = report .. 'Device Name:' .. dev_name .. '\r\n\r\n'
report = report .. 'Device Meta String:\r\n' .. meta_string .. '\r\n\r\n'
report = report .. 'Device Client Info:\r\n' .. json.encode(info) .. '\r\n\r\n'
report = report .. 'Device Client List:\r\n' .. json.encode(listing).. '\r\n\r\n'
report = report .. 'End of Report\r\n'

local success, reason = email(emailaddress,subject,report)
if success then
	debug('done, report has been emailed')
else
	debug('error sending, reason:'..reason)
end





