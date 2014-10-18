local input = alias['input']

local emailaddress = '<YOUR_EMAIL@ADDRESS_HERE'

debug('starting')

-- make a while loop that runs forever
-- to handle incoming data

while true do
  local ts = input.wait() -- this is a blocking function (it will wait forever)
  local value = input[ts] -- get the new value at this timestamp
  
  debug('got value: ' .. value)
  
  -- Check for condition
  if value > 90 then
    debug('high state detected!')
    email(emailaddress, 'High State Detected',string.format('Recorded a value of %d',value))
  end
end