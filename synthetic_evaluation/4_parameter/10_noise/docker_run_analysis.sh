python3 create_serial_analysis_script.py
chmod +x run_serial_analysis.sh
./run_serial_analysis.sh
mkdir accuracy_plots analysis_results cost_plots point_plots
mv result.budget.* analysis_results/
mv accuracy_b* accuracy_plots/
mv cost_b* cost_plots/
mv additional_points_b* point_plots/
python3 plot.py --bucket 5 --reps 2
python3 plot.py --bucket 10 --reps 2
python3 plot.py --bucket 15 --reps 2
python3 plot.py --bucket 20 --reps 2
mkdir results
mv accuracy_*.png results/
mv additional_points.png results/
mv cost.png results/
./archive.sh final
python3 single_plot.py --path final/analysis_results/ --name results_final --reps 4
python3 budget_usage_plot.py --path final/analysis_results/ --name budget_usage_final --reps 4
