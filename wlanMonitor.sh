#!/bin/bash
if ifconfig wlan0 | grep -q "inet 10\|inet 192\|inet 172" ; then
	echo "Seems ok"
	echo `date`
else
	echo "Network is down again, attempting to rejoin"
	echo `date`
	sudo ifdown wlan0
	sleep 10
	sudo ifup --force wlan0
	sleep 10
fi
