#!/usr/bin/python
# -* coding: utf-8 *-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# SolarMax API Developed 2009-2010 by Bernd Wurst <bernd@schokokeks.org>
# for own use.
# Released to the public in 2012.

# Combined 2014 Matt Cordell <Solar@snoyowie.com>

import time
import sys
from SolarMax.solarmax import SolarMax  # API for talking to the SolarMax inverter
from PVoutput.pvoutput import PVoutput_Connection  # API for talking to the PVoutput inverter


# Array of inverters in system. IP address and device number
# factory default is likely 192.168.1.123:12345 1
inverters = {'192.168.1.123': [1, ]}

# get pvoutput API details
apiDelay = 5  # time to delay after API calls
# API Key and SystemId must be entered as arguments for script.

if len(sys.argv) != 3:
    print "2 arguments required. API key and SystemId. See Documentation for details"
    print "example: $python SolarMax_PVoutLiveLog.py <API Key> <System Id> "
    exit()
else:
    pvo_key = str(sys.argv[1])
    pvo_systemid = str(sys.argv[2])

smlist = []
for host in inverters.keys():
    sm = SolarMax(host, 12345)  # using port 12345
    sm.use_inverters(inverters[host])
    smlist.append(sm)
allinverters = []
for host in inverters.keys():
    allinverters.extend(inverters[host])

# cycle through the known inverters
count = 0
for sm in smlist:
    for (no, ivdata) in sm.inverters().iteritems():
        try:
            # Pass the parameters you wish to get from the inverter and log. Power, Voltage and Temp are all that's required for PVoutput.
            (inverter, current) = sm.query(no, ['PAC', 'UL1', 'TKK'])

            # create connection to pvoutput.org
            pvoutz = PVoutput_Connection(pvo_key, pvo_systemid)

            #use system date/Time for logging. Close enough
            powerdate = time.strftime("%Y%m%d")
            powerTime = time.strftime("%H:%M")
            # parse the results of sm.query above
            PowerGeneration = str(current['PAC'])
            Temperature = str(current['TKK'])
            Voltage = str(current['UL1'])

            print "Date: " + str(powerdate) + " Time: " + str(
                powerTime) + " W: " + PowerGeneration + " temp: " + Temperature + " volt: " + Voltage

            # update pvoutput
            if (PowerGeneration):  # make sure that we have actual values...
                pvoutz.add_status(powerdate, powerTime, power_exp=PowerGeneration, temp=Temperature, vdc=Voltage)
                print "Sucessful Log "
                #Ensure API limits adhered to
                time.sleep(apiDelay)
            else:
                print "aint no data bitch.. make the sun come up"

            count += 1
        except:
            print 'Communication Error, WR %i' % no
            continue
#(status, errors) = sm.status(count)

#if errors:
#    print('WR %i: %s (%s)' % (no, status, errors))
#    try:
#        print("details: ", int(PAC), int(TEMP), int(VOLTAGE))
#    except:
#        pass

if count < len(allinverters):
    print 'Not all inverters queried (%i < %i)' % (count, len(allinverters))

print "Data Succesfully query and posted."
time.sleep(1)

