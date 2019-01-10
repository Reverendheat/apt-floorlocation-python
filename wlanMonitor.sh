#!/bin/bash
if ifconfig wlan0 | grep -q "inet 10\|inet 192\|inet 172" ; then
	echo `date`
	echo "Seems ok"
	echo
else
	echo `date`
	echo "Network is down again, attempting to rejoin"
	echo
	sudo ifconfig wlan0 down
	sleep 10
	sudo ifconfig wlan0 up
	sleep 10
fi
