now=`date '+%Y%m%d%H%M%S'`
filename="/home/pi/movesA${now}.csv"
echo $filename
sqlite3 -csv /home/pi/floorlocation.db "SELECT * FROM moves;" > $filename
sed -i 's/\"//g' $filename
if [ -z "$(ls -A /mnt/csvMove)" ]
then
        echo "Folders Empty, trying to mount, or check if DONTREMOVE.txt is missing from newmas share. Will try to copy again in one minute"
        sudo mount -t cifs //NEWMAS/FloorLocations/IncomingFiles/ /mnt/csvMove/ -o user=FLocations,password=%YOULLNEEDTOCHECKCW%
else
        echo "Folder Not Empty, attempting to copy"
        if [ -s $filename ]
        then
                echo 'File isnt empty, trying to copy and wipe database'
                sudo cp $filename /mnt/csvMove/
                sqlite3 /home/pi/floorlocation.db "DELETE FROM moves;"
        else
                echo 'Files empty, nothing is copying'
                sudo rm $filename
        fi
fi