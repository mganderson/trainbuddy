#!/bin/bash
# Michael Anderson
# 03/29/17

cat stops.txt | cut -d "," -f3 | cut -d "," -f1 > juststationnames.txt

tr A-Z a-z < juststationnames.txt >juststationnameslower.txt



