#!/bin/bash

#Bash script to run HRRRE_Finalize.py

date=$1 #Date of the run
IHR=$2 #Initialization hour of the run
mem=$3 #Model member
h=$4 #Actual run hour of the model

for mem in {1..9}
 do
  member=0$mem	  
  for h in {1..18}
  do

    if [ $h -lt 10 ]
    then
      h=$h
      h0=$((h - 1))
    else
      h=$h  
      h0=$((h - 1))
      if [ $h == 10 ]
      then      
        h0=$((h - 1))	      
      fi	      
    fi 
   python HRRRE_Finalized.py $date $IHR $mem $h $h0
 
    echo $date
    echo $IHR 
    echo $mem
    echo $h
    echo $h0

    done
 done    
