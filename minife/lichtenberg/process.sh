
mkdir accuracy_plots analysis_results cost_plots point_plots
rm er_b*
rm out_b*
rm analysis_job_b*
mv result.budget.* analysis_results/
mv accuracy_b* accuracy_plots/
mv cost_b* cost_plots/
mv additional_points_b* point_plots/
python plot.py --bucket 5 --reps 2
python plot.py --bucket 10 --reps 2
python plot.py --bucket 15 --reps 2
python plot.py --bucket 20 --reps 2
mkdir results
mv accuracy_*.png results/
mv additional_points.png results/
mv cost.png results/