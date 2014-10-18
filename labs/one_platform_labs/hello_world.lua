-- Hello World Lua Script

debug('hello world')

local i = 0

debug('value of i: '..tostring(i))

-- why does the following line cause an error?
j = 'two' -- string

debug('value of j: ' ..j)

-- the now variable provides the current unix timestamp
debug('Current unix timestamp:'.. now)

debug(string.format('Current Date/Time (UTC): %s',date())) -- date default's to UTC
settimezone("America/Chicago")  -- sets the script's timezone
debug(string.format('Current Date/Time (America/Chicago): %s',date())) 

local example_table = {foo='bar',timestamp=now,i=i}
debug(json.encode(example_table))


