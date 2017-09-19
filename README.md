# ikea-smartlight
python framework for controlling the Ikea smart lights (tradfri)
An easy setup guide to get the command line controls offered here is available here: http://kuehnast.com/s9y/archives/657-Manage-your-IKEA-TRDFRI-smart-lighting-system-with-Linux.html
(Note: this is not my article, but it's what got me started working on this project)

### requirements
at this moment there is no coap libs with dTLS, the ikea smart lights are using dTLS with coap for security. the only option is to build a new libcoap with dTLS included. libcoap requires `cunit, a2x, doxygen and dot` you need to install these requirements first.

when this is installed run the build script for compiling libcoap
```bash
cd bin
./build.sh
```

the framework also requires `tqdm` for showing progressbars, you could strip it from the sourcecode or install the module for python: `pip install pip --upgrade && pip install tqdm`.

### libcoap usage
```bash
# getting tradfri information
./coap-client -m get -u "Client_identity" -k "<key>" "coaps://<hup>:5684/15001"
# getting tradfri lightbulb status
./coap-client -m get -u "Client_identity" -k "<key>" "coaps://<hup>:5684/15001/65537"

# turn on tradfri lightbulb
./coap-client -m put -u "Client_identity" -k "<key>" -e '{ "3311" : [{ "5850" : 1 ]} }' "coaps://<hup>:5684/15001/65537"
# turn off tradfri lightbulb
./coap-client -m put -u "Client_identity" -k "<key>" -e '{ "3311" : [{ "5850" : 0 ]} }' "coaps://<hup>:5684/15001/65537"
```

### output
```
./tradfri-status.py
[ ] tradfri: requireing all tradfri devices, please wait ...
[+] tradfri: device information gathered
===========================================================

bulbid 65537, name: TRADFRI bulb E27, bightness: 1, state: off
bulbid 65538, name: TRADFRI bulb E27, bightness: 1, state: off
bulbid 65539, name: TRADFRI bulb E27, bightness: 1, state: off
bulbid 65540, name: TRADFRI bulb E27, bightness: 1, state: off
bulbid 65542, name: TRADFRI bulb E27, bightness: 1, state: off
bulbid 65541, name: TRADFRI bulb E27, bightness: 1, state: off
bulbid 65544, name: TRADFRI bulb E27, bightness: 254, state: off


groupid: 137274, name: hal beneden, state: off
groupid: 183216, name: slaapkamer, state: off
groupid: 140387, name: woonkamer, state: off
groupid: 186970, name: hal boven, state: off
```

### Running the server
Create a file server.cfg in the project root, following the format described in sampleserver.cfg. Then simply run
python3 server.py. A webserver will be started on the port you specified that serves light statuses, and can accept
POST request with JSON in the format
```
{
	"group":"mygroup",
	"state":"on"
}
or
{
	"group":"mygroup",
	"state":"50"
}
```
In the first case, "on" or "off" is accepted, while in the second case a brightness % is accepted

### todo
- [X] add change state (power on/off lightbulb)
- [X] add dimmer value (dimm lightbulb)
- [X] add change state group (power on/off groups)
- [X] add dimmer value group (dimm group)
- [X] add color temperature lightbulb (switch to cold, normal or warm)

### licensing and credits
ikea-smartlight is licensed under the GPLv3:
```
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

For the full license, see the LICENSE file.
```
