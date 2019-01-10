#!/bin/bash
if ifconfig wlan0 | grep -q "inet 10\|inet 192\|inet 172" ; then
	echo `date`
	echo "Seems ok"
else
	echo `date`
	echo "Network is down again, attempting to rejoin"
	sudo ifdown wlan0
	sleep 10
	sudo ifup --force wlan0
	sleep 10
fi
