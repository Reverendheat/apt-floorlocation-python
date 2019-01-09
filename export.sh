now=`date '+%Y%m%d%H%M%S'`
host = ${HOSTNAME: -3}
filename="/home/pi/$host${now}.csv"
echo `date`
echo $filename
sqlite3 -csv /home/pi/floorlocation.db "SELECT * FROM moves;" > $filename
sed -i "s/\"//g" $filename
if [ -z "$(ls -A /mnt/csvMove)" ]
then
	if [ ! -d /mnt/csvMove/ ]
	then
		sudo mkdir /mnt/csvMove/
	fi
        echo "/mnt/csvMove appears to be Empty, trying to mount, or check if DONTREMOVE.txt is missing from newmas share. Will try to copy again in one minute"
        sudo mount -t cifs //NEWMAS/FloorLocations/IncomingFiles/ /mnt/csvMove/ -o user=FLocations,password=APT.248.YEAH.BOI
else
        echo "/mnt/csvMove not empty, attempting to copy"
        if [ -s $filename ]
        then
                echo "$filename isnt empty, trying to copy and wipe database"
                sudo cp $filename /mnt/csvMove/
                sqlite3 /home/pi/floorlocation.db "DELETE FROM moves;"
		sleep 5
		sudo rm $filename
	else
                echo "$filename is empty, nothing is copying"
		sleep 5
                sudo rm $filename
	fi
fi
#for some reason, some files would remain and be empty, this should remove those from now on
if ls /home/pi/*.csv
then
	for csv in /home/pi/*.csv; do
		if [ -s "$csv" ]
		then
			echo "$csv is not empty.."
		else
			rm -f $csv
			echo "Removed $csv since it was empty..."
		fi
	done
else
	echo "No csv files exist currently in /home/pi/"
fi
echo "\n"
