#!/bin/bash
IP=$1
ROW=$2
COL=$3
count=$2*$3
for((i=1;i<=6;i+=1));do
	python wxform.py $i &done

