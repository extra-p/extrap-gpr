prefix=relearn

P_VALUES="32 64 128 256 512"
SIZE_VALUES="5000 6000 7000 8000 9000"
THETA_VALUES="0.1"
KERNELS=("  main()" "  Initialization" "  Simulation loop" "    Update electrical activity" "    Update #synaptic elements delta" "    Connectivity update" "      Update #synaptic elements + del synapses" "      Update local trees" "      Exchange branch nodes (w/ Allgather)" "      Insert branch nodes into global tree" "      Update global tree" "      Find target neurons (w/ RMA)" "      Empty remote nodes cache" "      Create synapses (w/ Alltoall)")
FILENAME="relearn.txt"

echo PARAMETER p >> $FILENAME
echo PARAMETER n >> $FILENAME
echo "" >> $FILENAME

for p in $P_VALUES
do
    for n in $SIZE_VALUES
    do
        echo "POINTS ( $p $n )" >> $FILENAME
    done
done

echo "" >> $FILENAME
echo "METRIC time" >> $FILENAME
echo "" >> $FILENAME

for kernel in "${KERNELS[@]}"
do
    echo "REGION $kernel" >> $FILENAME

    for p in $P_VALUES
    do
        for size in $SIZE_VALUES
        do
            LINE="DATA "
            
            for theta in $THETA_VALUES
            do
                
                LINE="$LINE `grep "$kernel" ${prefix}_p${p}_size${size}_theta${theta}*.out | head -n 1 | cut -f3 -d \| | cut -f2 -d " "`"
                LINE="$LINE `grep -m2 "$kernel" ${prefix}_p${p}_size${size}_theta${theta}*.out | tail -n 1 | cut -f3 -d \| | cut -f2 -d " "`"
                
            done
            
            echo $LINE >> $FILENAME
            
        done
    done

    echo "" >> $FILENAME

done
