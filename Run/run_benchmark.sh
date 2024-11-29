#!/bin/bash
MOD=$2
OFF=$1
STIME=300
MEMLIMIT=8192

T=$(($(grep -v "#" testfile | wc -l)-1))
for i in $(seq 0 $T)
do
	cmd=$(($i+1))"q;d"
	line=`grep -v "#" testfile | sed $cmd`
	tests[i]=$(echo $line | cut -d';' -f1)
	params[i]=$(echo $line | cut -d';' -f2)
	testdirs[i]=$(echo $line | cut -d';' -f3)
done


FILTER="!((NR+$OFF)%$MOD)"

TMPDIR="tmprerun3"
# NFSDIR="/home/wallner/Downloads/tmp-supp/results"
# INSDIR="/home/wallner/Downloads/tmp-supp/instances/"
NFSDIR="results_rerun3"

INSDIR="/home/andreipopi/Documents/GitLab/pbaf-treedec/InstanceGenerator/instance_set"

#sudo mkdir -p $TMPDIR
#sudo mkdir -p $NFSDIR

#mkdir -p $INSDIR

#cd software

N=${#tests[@]}

for i in $(seq 0 $N)
do
    mkdir -p $TMPDIR'/'${testdirs[$i]}
	mkdir -p $NFSDIR'/'${testdirs[$i]}
done

for INSTANCE in $(find $INSDIR -type f | grep ".lp"$ | sort | awk $FILTER)
do
	echo $INSTANCE
# 	for i in $(seq 0 $((($N-1)/2))) # MUST HAVE EVEN NUMBER OF TESTS 
	for i in $(seq 0 $(($N-1))) # MUST HAVE EVEN NUMBER OF TESTS 
	do
		T1=$i
		# T2=$((2*$i+1))

		LOGFILE1=$TMPDIR'/'${testdirs[$T1]}'/'$(basename $INSTANCE)'.'${testdirs[$T1]}'.log'
		# LOGFILE2=$TMPDIR'/'${testdirs[$T2]}'/'$(basename $INSTANCE)'.'${testdirs[$T2]}'.log'

		NFSFILE1=$NFSDIR'/'${testdirs[$T1]}'/'$(basename $INSTANCE)'.'${testdirs[$T1]}'.log'
		# NFSFILE2=$NFSDIR'/'${testdirs[$T2]}'/'$(basename $INSTANCE)'.'${testdirs[$T2]}'.log'

		PID1=""
		# PID2=""
		
		if [ -f $NFSFILE1 ]
		then
			echo "logfile exists"
		else
			echo ${tests[$T1]}" "${params[$T1]}
			# ADDITIONAL1=`cat $INSTANCE`
			# TEMPNAME1=${INSTANCE%.*}
			# AFINSTANCE1=${TEMPNAME1%.*}
#                         ADFINSTANCE1=$INSTANCE
# 			(ulimit -St $STIME ; { /usr/bin/time -v ${tests[$T1]} $ADFINSTANCE1 ; } 1> $LOGFILE1 2>&1) &
			
			({ /usr/bin/time -v ./runsolver -C $STIME --vsize-limit $MEMLIMIT ${tests[$T1]} ${params[$T1]} $INSTANCE ; } 1> $LOGFILE1 2>&1) &
			PID1=$!
			taskset -pc 0 $PID1 > /dev/null
		fi

		# if [ -f $NFSFILE2 ]
		# then
		#	echo "logfile exists"
		# else
		#	echo ${tests[$T2]}" "${params[$T2]}
		#	ADDITIONAL2=`cat $INSTANCE`
		#	TEMPNAME2=${INSTANCE%.*}
		#	AFINSTANCE2=${TEMPNAME2%.*}
		#	(ulimit -St $STIME ; { /usr/bin/time -v ${tests[$T2]} -f $AFINSTANCE2 -a $ADDITIONAL2 ${params[$T2]}; } 1> $LOGFILE2 2>&1) &
		#	PID2=$!
		#	taskset -pc 1 $PID2 > /dev/null
		# fi

		wait $PID1 # $PID2

		if [ ! -f $NFSFILE1 ]
		then
			cp $LOGFILE1 $NFSDIR'/'${testdirs[$T1]}'/'
		fi

		# if [ ! -f $NFSFILE2 ]
		# then
		#	cp $LOGFILE2 $NFSDIR'/'${testdirs[$T2]}'/'
		# fi

	done
done
