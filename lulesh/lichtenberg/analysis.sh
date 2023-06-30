#!/bin/bash
cd ..

for i in {14..100}
do
    python .\case_study.py --cube E:\lulesh\ --processes 0 --parameters "p","s" --eval_point "1000","35" --filter 0 --budget $i --normalization True
done

#min budget lulesh 14.4
