#!/bin/bash
ip=$1
row=$2
col=$3
x=0
y=0
i=0

for((r=1;r<=row;r+=1));
do
	y=$((r-1))
	y=$((y*220))
	y=$((y+20))
	if [ "$y" -gt 440 ]; then
		y=$((y-9))
	fi
	for((c=1;c<=col;c+=1));
	do
		i=$((i+1))
		x=$((c-1))
		x=$((x*328))
		x=$((x+20))
		python wxform.py $i $ip $x $y &done
#!		echo $i
#!		echo $x
#!		echo $y
	done
	x=0
done

