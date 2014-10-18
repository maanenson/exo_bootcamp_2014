-- This script generates randomized sensor data with a controlled range,
-- and also has the feature to be able to have sensor values "wander"
-- towards defined set points.
-- 
-- This script also will create the necessary dataports if they do not exist.
-- 


debug('starting')

-- table of dataports to create if not already in existance
local dstable = {
  {alias="emulator_timer",name="Emulator Timer",format="integer"},
  {alias="temperature",name="Temperature",format="float"},
  {alias="humidity",name="Humidity",format="float"},
  {alias="set_point",name="Set Points",format="string",},
}

-- This routine checks to see if each item listed in the dstable 
-- is a dataport under this client, otherwise creates it using 
-- the manage.create scripting API
--
debug('checking and adding data ports')
for i, ds in ipairs(dstable) do
  if not manage.lookup("aliased" ,ds.alias) then
    local description = {
      format = ds.format
     ,name = ds.name
     ,retention = {count = "infinity" ,duration = "infinity"}
     ,visibility = "private"
    }
    local success ,rid = manage.create("dataport" ,description)
    if not success then
      debug("error initializing rid dataport: "..rid or "")
      log.value = "init error initializing dataport: "..ds.alias or "init error initializing dataport"
    else
      manage.map("alias" ,rid ,ds.alias)
    end
  end
end

-- Ok, now get variable aliases for the dataports
local emulator_timer = alias['emulator_timer']
local temperature = alias['temperature']
local humidity    = alias['humidity']

-- How often should data be written? WAIT is measured in seconds.
local WAIT = 10

-- When a new randomized data point is generated, and the set point is lower
-- than the current value, what is the min/max range that should be used as
-- inputs to the random number generator? The absolute value of DMIN should be
-- larger than the absolute value of DMAX. The wider the range, the more
-- variability there will be.
local DMIN = -2 -- Should be negative
local DMAX = 1  -- Should be possitive

-- UMIN and UMAX work the same as DMIN and DMAX, but are only used when the 
-- set point for the data source is higher than the current value. The absolute
-- value of UMIN should be smaller than the absolute value of UMAX. The wider the
-- range, the more variability there will be.
local UMIN = -1
local UMAX = 2

-- Function to generate a random number within a range. If x is 0 and y is 1, the
-- value will be a flow. In all other cases, the number will be an integer within
-- the range {x,y}.
local function rand(x,y)
    return math.random(x,y)  
end

-- Function to generate the next data point as a function of the current data value,
-- and the next data value. The constants DMIN/DMAX and UMIN/UMAX are used to constrain
-- the amount of variability in the samples.
local function new(current,target)
    if current == nil then
        current = target
    end
    if current < target then
        return current + rand(UMIN, UMAX)
    else
        return current + rand(DMIN, DMAX)
    end
end

-- Function to convert Fahrenheit to Celsius. This is needed in this script
-- since the values for temperature in this example are written to the platform
-- in Celsius, but converted to Fahrenheit. When the values are subsequently 
-- read from the platform, they are in Fahrenheit. However, it becomes difficult
-- To read/write values to the platform when the units are different.
--
-- Therefore, because this script was developed for an example application that
-- used temperature, this function was needed.
local function f2c(f)
    return (f - 32) * 5/9  
end

-- Initial local variables with values that are sensible defaults. 
local t_set = 20 -- 20 degrees C (room temp)
local h_set = 50 -- 50% relative humidity

-- Now that the script has been initialized, enter the forever busy-wait loop
while true do
  
    -- Use a unused dataport to wait on, which will timeout at now+WAIT seconds and then run
    local ts1 = emulator_timer.wait(now+WAIT)

    -- Set the temperature, and humidity data sources with new values
    -- that are randomized, yet moving towards defined set points.
    --
    temperature.value = new(temperature.value, t_set)
    humidity.value = new(humidity.value, h_set)
  
    debug("Updated values: " .. temperature.value .. ", " .. humidity.value)
end