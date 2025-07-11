# :fax: ESCPOS Thermal Printer Webserver

Simple Webserver using Sockets designed to add WiFi functionality to POS Printers, with use of a Raspberry Pi or similar.

## Installation
Designed for Raspberry Pi

Should run on any Debian (Or Close) Device that has WiFi, and supports Python, and has two cores. (No Guarantees)

Should also run on Arch or Ubuntu, but is :warning: untested.
## Installation Instructions
- Download
- Swap PID and VID to that of your individual printer. `Default are for a EPSON TM-T20IIIL`

  (They are easiest to find via `lsusb`, however Windows Device Manager will also show them if you dig through properties.)
- Setup a `systemctl` Service or Similar (Optional)
- Run

## Features/Usage

#### Queuing
If the printer cannot be reached, default behavior is to queue messages for when it can.
#### Printing
The webserver simply prints anything sent to the correct port via a POST, and then cuts the paper.*
#### Authentication
The webserver's default behavior has been updated to only print requests from devices that embed the correct user-specified secret key in the header of the request.

Secret key should be prepended as "Authorization: [KEY]", and match the key held by the printer.

Default printer key location is ./key, the file should only contain a copy of the secret key.

#### Default Ports
- `9100`: Responds to POST Requests by Printing Message Contents
- `8080`: Basic Health Check, Returns '200 OK' if Online

*Server is designed to run locally, and absolutely should NEVER be exposed to WAN.

~~Server WILL print anything sent to `9100` (Or Custom Port) via a POST request.~~

Server will now only print from a device that properly embeds a matching token in the header, however this is able to be disabled, and trivial to break depending on user-specified secret key strength.
