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

    b1 = plt.bar(X_axis - 0.3, full, 0.2, label = 'Full matrix points')
    b2 = plt.bar(X_axis - 0.1, generic, 0.2, label = 'Generic strategy')
    b3 = plt.bar(X_axis+0.1, gpr, 0.2, label = 'GPR strategy')
    b4 = plt.bar(X_axis + 0.3, hybrid, 0.2, label = 'Hybrid strategy')

    plt.bar_label(b1, label_type='edge', fontsize=8)
    plt.bar_label(b2, label_type='edge', fontsize=8)
    plt.bar_label(b3, label_type='edge', fontsize=8)
    plt.bar_label(b4, label_type='edge', fontsize=8)
    
    plt.xticks(X_axis, X)
    plt.xlabel("Accuracy buckets")
    plt.ylabel("Percentage of models [%]")
    plt.title("Percentage of models in each accuracy bucket")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.savefig('accuracy_b'+str(budget)+'.png')
    #plt.show()
    plt.close()

def plot_costs(used_costs, base_budget, budget):
    """mean_budget_generic = float("{:.2f}".format(mean_budget_generic))
    mean_budget_gpr = float("{:.2f}".format(mean_budget_gpr))
    mean_budget_hybrid = float("{:.2f}".format(mean_budget_hybrid))
    langs = ["full", "generic", "gpr", "hybrid\n(generic+gpr)"]
    cost = [100, mean_budget_generic, mean_budget_gpr, mean_budget_hybrid]
    b1 = plt.bar(langs, cost, 0.4)
    plt.bar_label(b1, label_type='edge')
    plt.xticks(np.arange(len(langs)), langs)
    plt.xlabel("masurement point selection strategy")
    plt.ylabel("percentage of budget [%]")
    plt.title("Modeling budget used by each strategy to achieve outlined accuracy")
    plt.tight_layout()
    plt.savefig('cost.png')
    plt.show()"""
    langs = ["full", "generic", "gpr", "hybrid\n(generic+gpr)"]
    fig, ax = plt.subplots()
    bottom = np.zeros(4)
    bars = []
    for boolean, add_point in used_costs.items():
        p = ax.bar(langs, add_point, 0.5, label=boolean, bottom=bottom)
        bottom += add_point
        bars.append(p)
    ax.bar_label(p, label_type='edge')
    ax.legend(loc="upper right")
    # draw labels for individual bar parts
    for i in range(len(langs)):
        b = p[i]
        w,h = b.get_width(), b.get_height()
        x0, y0 = b.xy
        x2, y2 = x0,y0+h
        d=y2-y0
        yt=y0+(d/2)
        d=h-y2
        yt2=y0/2
        ax.text(langs[i], yt2, str("{:.2f}".format(base_budget)))
        ax.text(langs[i], yt, str("{:.2f}".format(add_point[i])))
    plt.xlabel("masurement point selection strategy")
    plt.ylabel("percentage of budget [%]")
    plt.title("Modeling budget used by each strategy to achieve outlined accuracy")
    plt.tight_layout()
    plt.savefig('cost_b'+str(budget)+'.png')
    #plt.show()
    plt.close()

def plot_measurement_point_number(add_points, min_points, budget):
    langs = ["full", "generic", "gpr", "hybrid\n(generic+gpr)"]
    fig, ax = plt.subplots()
    bottom = np.zeros(4)
    bars = []
    for boolean, add_point in add_points.items():
        p = ax.bar(langs, add_point, 0.5, label=boolean, bottom=bottom)
        bottom += add_point
        bars.append(p)
    ax.bar_label(p, label_type='edge')
    ax.legend(loc="upper right")
    # draw labels for individual bar parts
    for i in range(len(langs)):
        b = p[i]
        w,h = b.get_width(), b.get_height()
        x0, y0 = b.xy
        x2, y2 = x0,y0+h
        d=y2-y0
        yt=y0+(d/2)
        d=h-y2
        yt2=y0/2
        ax.text(langs[i], yt2, str("{:.2f}".format(min_points)))
        ax.text(langs[i], yt, str("{:.2f}".format(add_point[i])))
    plt.xlabel("measurement point selection strategy")
    plt.ylabel("additional measurement points")
    plt.title("Number of measurement points used by each\n strategy to achieve outlined accuracy")
    plt.tight_layout()
    plt.savefig('additional_points_b'+str(budget)+'.png')
    #plt.show()
    plt.close()