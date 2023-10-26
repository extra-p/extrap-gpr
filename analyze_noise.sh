mkdir noise_analysis
cd noise_analysis
python ../noise_analysis.py --text ../relearn/relearn_data.txt --total-runtime 31978.682999999997 --name relearn
python ../noise_analysis.py --cube /work/scratch/mr52jiti/data/lulesh/ --name lulesh
python ../noise_analysis.py --cube /work/scratch/mr52jiti/data/fastest/ --name fastest
python ../noise_analysis.py --cube /work/scratch/mr52jiti/data/kripke/ --name kripke
python ../noise_analysis.py --cube /work/scratch/mr52jiti/data/minife/ --name minife
python ../noise_analysis.py --cube /work/scratch/mr52jiti/data/quicksilver/ --name quicksilver
python ../plot_noise.py