#!/bin/bash

#Bash script to run HREFCode.py

date=$1 #Date of the run
IHR=$2 #Initialization hour of the run
mem=$3 #Name of the model member
h=$4 #Actual run hour of the model
h0=$5 #One hour less than h

#Declare a string array of the HREF member names

declare -a MemberList=("hrwarwtl00" "hrwarwtl01" "hrwnmmbtl00" "hrwnmmbtl01" "hrwnssltl00" "hrwnssltl01" "namnesttl00" "namnesttl01")

for mem in ${MemberList[@]};
  do
    for h in {1..18}
      do
        if [ $h -lt 10 ]
	then
  	  h=$h
	  h0=$((h - 1))
	else
	  h=$h
	  h0=$((h - 1))
	fi

	python HREFCode.py $date $IHR $mem $h $h0

	echo $date
	echo $IHR
	echo $mem
	echo $h
	echo $h0

	done
      done
