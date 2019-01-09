now=`date '+%Y%m%d%H%M%S'`
filename="/home/pi/A${now}.csv"
echo $filename
echo `date`
sqlite3 -csv /home/pi/floorlocation.db "SELECT * FROM moves;" > $filename
sed -i 's/\"//g' $filename
if [ -z "$(ls -A /mnt/csvMove)" ]
then
        echo "Folders Empty, trying to mount, or check if DONTREMOVE.txt is missing from newmas share. Will try to copy again in one minute"
        sudo mount -t cifs //NEWMAS/FloorLocations/IncomingFiles/ /mnt/csvMove/ -o user=FLocations,password=APT.248.YEAH.BOI
else
        echo "Folder Not Empty, attempting to copy"
        if [ -s $filename ]
        then
                echo 'File isnt empty, trying to copy and wipe database'
                sudo cp $filename /mnt/csvMove/
                sqlite3 /home/pi/floorlocation.db "DELETE FROM moves;"
		sleep 5
		sudo rm $filename
	else
                echo 'Files empty, nothing is copying'
		sleep 5
                sudo rm $filename
	fi
fi
#for some reason, some files would remain and be empty, this should remove those from now on
for csv in /home/pi/*.csv; do
	if [ -s $csv ]
	then
		rm -f $csv
		echo 'Removed empty file $csv'
	else
		echo '$ not empty...'
	fi
done
