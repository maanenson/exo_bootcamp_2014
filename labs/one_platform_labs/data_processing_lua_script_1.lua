local output = alias['output']
local input = alias['input']


debug('starting')

-- EXAMPLE PROCESSING 
local function process(value)
  if value == nil or type(value) ~= 'number' then
    -- bad data
    return
  elseif value > 1000 or value < 0 then
    -- throw away values
    debug('outside scope')
    return
  else
    -- Process your data - this basic example converts to percentage
    local percentage = value / 1000 * 100
    return percentage
  end
end

-- CONTINOUS RUNNING ROUTINE TO HANDLE NEW VALUES
while true do
  local ts = input.wait()
  local ret = process(input[ts])
  if ret ~= nil then
    --debug('output value: '.. ret)
    output[ts] = ret
  else
    debug('bad data')
  end
end