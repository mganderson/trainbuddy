#!/bin/bash
# Michael Anderson

while read line
do
	echo "$line,$line"
done < $1
