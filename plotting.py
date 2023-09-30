from matplotlib import pyplot as plt
import numpy as np

def plot_model_accuracy(percentage_bucket_counter_full, percentage_bucket_counter_generic, percentage_bucket_counter_gpr, percentage_bucket_counter_hybrid, budget):
    X = ['+-5%','+-10%','+-15%','+-20%']
    full = [percentage_bucket_counter_full["5"], 
            percentage_bucket_counter_full["10"], 
            percentage_bucket_counter_full["15"], 
            percentage_bucket_counter_full["20"]]
    generic = [percentage_bucket_counter_generic["5"],
                percentage_bucket_counter_generic["10"],
                percentage_bucket_counter_generic["15"],
                percentage_bucket_counter_generic["20"]]
    gpr = [percentage_bucket_counter_gpr["5"],
                percentage_bucket_counter_gpr["10"],
                percentage_bucket_counter_gpr["15"],
                percentage_bucket_counter_gpr["20"]]
    hybrid = [percentage_bucket_counter_hybrid["5"],
                percentage_bucket_counter_hybrid["10"],
                percentage_bucket_counter_hybrid["15"],
                percentage_bucket_counter_hybrid["20"]]

    X_axis = np.arange(len(X))
    
    plt.figure(figsize=(10,6))

    budget_string = "{:0.1f}".format(budget)

    b1 = plt.bar(X_axis - 0.3, full, 0.2, label = 'Full matrix points (budget=100%)', hatch="\\\\", edgecolor='black',)
    b2 = plt.bar(X_axis - 0.1, generic, 0.2, label = 'Generic strategy (budget='+str(budget_string)+'%)', edgecolor='black',)
    b3 = plt.bar(X_axis+0.1, gpr, 0.2, label = 'GPR strategy (budget='+str(budget_string)+'%)', hatch="//", edgecolor='black',)
    b4 = plt.bar(X_axis + 0.3, hybrid, 0.2, label = 'Hybrid strategy (budget='+str(budget_string)+'%)', hatch="xx", edgecolor='black',)

    plt.bar_label(b1, label_type='edge', fontsize=10, rotation=90, fmt='%0.2f', padding=4)
    plt.bar_label(b2, label_type='edge', fontsize=10, rotation=90, fmt='%0.2f', padding=4)
    plt.bar_label(b3, label_type='edge', fontsize=10, rotation=90, fmt='%0.2f', padding=4)
    plt.bar_label(b4, label_type='edge', fontsize=10, rotation=90, fmt='%0.2f', padding=4)
    
    plt.xticks(X_axis, X)
    plt.xlabel("Accuracy buckets")
    plt.ylabel("Percentage of models in bucket")
    plt.title("Percentage of models in each accuracy bucket", pad=25)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.savefig('accuracy_b'+str(budget_string)+'.png')
    #plt.show()
    plt.close()

def plot_costs(used_costs, base_budget, budget):
    langs = ["Full matrix", "Generic", "GPR", "Hybrid"]
    fig, ax = plt.subplots()
    bottom = np.zeros(4)
    bars = []
    plt.yscale("symlog")
    count = 0
    for boolean, add_point in used_costs.items():
        if count == 0:
            p = ax.bar(langs, add_point, 0.5, label=boolean, bottom=bottom, hatch="//", edgecolor="black")
        else:
            p = ax.bar(langs, add_point, 0.5, label=boolean, bottom=bottom, edgecolor="black")
        bottom += add_point
        count += 1
        bars.append(p)
    ax.bar_label(p, label_type='edge', fmt='%0.2f')
    ax.legend(loc="upper right")
    # draw labels for individual bar parts
    for i in range(len(langs)):
        b = p[i]
        w,h = b.get_width(), b.get_height()
        x0, y0 = b.xy
        x2, y2 = x0,y0+h
        text_x = x0 + 0.5*b.get_width() - 0.1
        d=y2-y0
        yt=y0+(d/2)*0.5
        d=h-y2
        yt2=y0/2*0.5
        ax.text(text_x, yt2, str("{:.2f}".format(base_budget)), color="white")
        ax.text(text_x, yt, str("{:.2f}".format(add_point[i])))
    budget_string = "{:0.1f}".format(budget)
    plt.xlabel("Measurement point selection strategy")
    plt.ylabel("Average used budget [%]")
    plt.title("Modeling budget used by each strategy (budget="+str(budget_string)+"%)")
    plt.tight_layout()
    plt.savefig('cost_b'+str(budget_string)+'.png')
    #plt.show()
    plt.close()

def plot_measurement_point_number(add_points, min_points, budget):
    langs = ["Full matrix", "Generic", "GPR", "Hybrid"]
    fig, ax = plt.subplots()
    bottom = np.zeros(4)
    bars = []
    count = 0
    for boolean, add_point in add_points.items():
        if count == 0:
            p = ax.bar(langs, add_point, 0.5, label=boolean, bottom=bottom, hatch="//", edgecolor="black")
        else:
            p = ax.bar(langs, add_point-min_points, 0.5, label=boolean, bottom=bottom, edgecolor="black")
        bottom += add_point
        count += 1
        bars.append(p)
    ax.bar_label(p, label_type='edge', fmt='%0.2f')
    ax.legend(loc="upper right")
    # draw labels for individual bar parts
    for i in range(len(langs)):
        b = p[i]
        w,h = b.get_width(), b.get_height()
        x0, y0 = b.xy
        text_x = x0 + 0.5*b.get_width() - 0.1
        x2, y2 = x0,y0+h
        d=y2-y0
        yt=y0+(d/2)
        d=h-y2
        yt2=y0/2
        ax.text(text_x, yt2, str("{:.2f}".format(min_points)), color="white")
        ax.text(text_x, yt, str("{:.2f}".format(add_point[i]-min_points)))
    plt.xlabel("Measurement point selection strategy")
    plt.ylabel("Average number of used measurement points")
    plt.title("Number of measurement points used by each strategy")
    plt.tight_layout()
    budget_string = "{:0.1f}".format(budget)
    plt.savefig('additional_points_b'+str(budget_string)+'.png')
    #plt.show()
    plt.close()