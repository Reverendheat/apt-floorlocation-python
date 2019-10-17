# apt-floorlocation-python
Floor location CLI Application to replace paper moves sheets.

### APTFloorLocation.py
This script is installed on Raspberry PI 3's mounted to ForkLifts. Once users log in, they will scan various finished goods that need to be moved around the factories. After finished goods scan AND a source and destination scan has been completed, the data is saved to a local SQLITE database on the PI. Every minute a cron job called Export.sh is called to push the data back to a MS SQL server, containing the "bins" of finished goods moved, the source/destination, date, and the employee who moved them. There are also a quicklist of commands taped to the lifts so they can easily scan without having to type.

### Export.SH
This shell script looks to see if the CIFS share is mounted, and if anything has been added to the database since it last ran. It will then move export the data from SQLITE and push the CSV up to the server.

### WLAN.SH
This shell script runs every 2 mintues to check if the wireless is still up, if not it will bring the WLAN interface down and back up to attempt to reconnect.

### heartbeat.py 
This script reaches out periodically to NodeJS server to report its script version, and the last time it was online. This can be viewed from a browser via apt-floorlocation-nodejs.
