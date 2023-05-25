from matplotlib import pyplot as plt
import numpy as np

def plot_measurement_point_number(agg_tips):
  
    fig, ax = plt.subplots()

    colors = ['#FFA500', '#FF0000']
    bottom = np.zeros(len(agg_tips))

    print("agg_tips.columns:",agg_tips.columns)

    agg_tips.columns = sorted(agg_tips.columns, reverse=True)

    print("agg_tips.columns:",agg_tips.columns)
    #TODO: that does not change something...

    for i, col in enumerate(agg_tips.columns):
        print("agg_tips.index:",agg_tips.index)
        print("col:",col)
        ax.bar(
        agg_tips.index, agg_tips[col], bottom=bottom, label=col, color=colors[i])
        bottom += np.array(agg_tips[col])

    totals = agg_tips.sum(axis=1)
    y_offset = 1
    for i, total in enumerate(totals):
        ax.text(totals.index[i], total + y_offset, total, ha='center',
            weight='bold')

    # Let's put the annotations inside the bars themselves by using a
    # negative offset.
    y_offset = -15
    # For each patch (basically each rectangle within the bar), add a label.
    for bar in ax.patches:
        ax.text(
        # Put the text in the middle of each bar. get_x returns the start
        # so we add half the width to get to the middle.
        bar.get_x() + bar.get_width() / 2,
        # Vertically, add the height of the bar to the start of the bar,
        # along with the offset.
        bar.get_height() + bar.get_y() + y_offset,
        # This is actual value we'll show.
        round(bar.get_height()),
        # Center the labels and style them a bit.
        ha='center',
        color='black',
        weight='bold',
        size=8
    )

    ax.legend(loc="upper right")
    plt.xlabel("measurement point selection strategy")
    plt.ylabel("additional measurement points")
    plt.title("Number of measurement points used by each\n strategy to achieve outlined accuracy")
    plt.tight_layout()
    plt.savefig('additional_points.png')
    plt.show()

