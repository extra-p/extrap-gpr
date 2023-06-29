#!/bin/bash
cd ..

for i in {17..100}
do
    python case_study.py --text relearn/relearn_data.txt --processes 0 --parameters "p","n" --eval_point "512","9000" --filter 0 --budget $i --normalization True
done

#min budget relearn 17.47
