#!/bin/bash
now=`date '+%Y%m%d%H%M%S'`
filename="/home/pi/wipcsv/${HOSTNAME: -3}${now}.csv"
echo `date`
echo $filename
if [ -z "$(ls -A /mnt/wipcsvMove)" ]
then
	if [ ! -d /mnt/wipcsvMove/ ]
	then
		sudo mkdir /mnt/wipcsvMove/
	fi
        echo "/mnt/wipcsvMove appears to be Empty, trying to mount, or check if DONTREMOVE.txt is missing from newmas share. Will try to copy again in one minute"
        sudo mount -t cifs //NEWMAS/FloorLocations/IncomingWIPfIles/ /mnt/wipcsvMove/ -o user=FLocations,password=APT.248.YEAH.BOI
else
        echo "/mnt/wipcsvMove not empty, attempting to copy"
	sqlite3 -csv /home/pi/floorlocation.db "SELECT * FROM wipfl;" > $filename
	sed -i "s/\"//g" $filename
        if [ -s $filename ]
        then
                echo "$filename isnt empty, trying to copy and wipe database"
                sudo cp $filename /mnt/wipcsvMove/
                sqlite3 /home/pi/floorlocation.db "DELETE FROM wipfl;"
		sleep 5
		sudo rm $filename
	else
                echo "$filename is empty, nothing is copying"
		sleep 5
                sudo rm $filename
	fi
fi
#for some reason, some files would remain and be empty, this should remove those from now on
if ls /home/pi/wipcsv/*.csv
then
	for csv in /home/pi/wipcsv/*.csv; do
		if [ -s "$csv" ]
		then
			echo "$csv is not empty.."
		else
			rm -f $csv
			echo "Removed $csv since it was empty..."
		fi
	done
else
	echo "No csv files exist currently in /home/pi/wipcsv"
fi
echo
