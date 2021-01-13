#!/bin/bash

#Bash script to run Obs_Data.py

date=$1 #Date of event
IHR=$2 #Initialization of observation
h=$3 #Actual run hour of the observation

dir="./0${date}_${IHR}/ObsData"

for f in $dir/*.asc
 do 

   python Obs_Data_Fixed.py $f $date $IHR

   echo $f
 done 
