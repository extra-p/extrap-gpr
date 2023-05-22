prefix=relearn

P_VALUES="32 64 128 256 512"
SIZE_VALUES="5000 6000 7000 8000 9000"
THETA_VALUES="0.1 0.2 0.3 0.4 0.5" 

for p in $P_VALUES
do
    for size in $SIZE_VALUES
    do
        LINE=""
        
        for theta in $THETA_VALUES
        do
            LINE="$LINE `grep "  Connectivity update" ${prefix}_p${p}_size${size}_theta${theta}*.out | head -n 1 | cut -f3 -d \| | cut -f2 -d " "`"
        done
        
        echo $LINE
    done

    echo
done
