# :fax: ESCPOS Thermal Printer Webserver

## Installation
Designed for Raspberry Pi

Should run on anything that has WiFi, and supports python, and has two cores. (No Guarantees)
## Installation Instructions
- Download
- Swap PID and VID to that of your individual printer.

  (They are easiest to find via `lsusb`, however Windows Device Manager will also show them if you dig through properties.)
- Setup a `systemctl` Service or Similar (Optional)
- Run

## Features/Usage

#### Queuing
If the printer cannot be reached, default behavior is to queue messages for when it can.
#### Printing
The webserver simply prints anything sent to the correct port via a POST, and then cuts the paper.*

#### Default Ports
- `9100`: Responds to POST Requests by Printing Message Contents
- `8080`: Basic Health Check, Returns '200 OK' if Online

*Server is designed to run locally, and absolutely should NEVER be exposed to WAN.

*Server WILL print anything sent to `9100` (Or Custom Port) via a POST request.
