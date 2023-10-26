import json
from os import listdir
from os.path import isfile, join
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
plt.rc('font', **{'family': 'sans-serif', 'size': 7.5})
plt.rc('text', usetex=True)
plt.rc('axes', edgecolor='black', linewidth=0.4, axisbelow=True)
plt.rc('xtick', **{'direction': 'out', 'major.width': 0.4})
plt.rc('ytick', **{'direction': 'in', 'major.width': 0.4})

def load_file(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data

def read_files(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    if "noise_level_dist.pdf" in onlyfiles:
        onlyfiles.remove("noise_level_dist.pdf")
    return onlyfiles

def plot_noise(dataset):

    data = []
    names = []
    for i, (name, values, percentages) in enumerate(dataset):
        x = []
        y = []

        cutoffrate = 0

        for i in range(len(values)):
            if percentages[i] > cutoffrate:
                x.append(values[i])
                y.append(percentages[i])
        data.append(x)
        names.append(name)
        
    cm = 1/2.54 
    plt.figure(figsize=(18.5*cm, 4*cm), dpi=300)
    # print(str(len(y))+" kernels used from "+str(len(values)))
    ylabel = plt.ylabel("Noise $n$ [$\%$]\nRange of relative deviation")
    x, y = ylabel.get_position()
    ylabel.set_position((x, y-0.05))
    # plt.ylabel("percentage of total runtime of the kernel")
    arrowstyle = {'arrowstyle': '-',
                  'relpos': (0, 0.5), 'shrinkA': 0, 'shrinkB': 5, 'linewidth': 0.4}

    violins = plt.violinplot(data, [1, 2, 3, 4, 5, 6])
    for b in violins['bodies']:
        b.set_facecolor((0, 0, 255 / 255, 1))
        b.set_alpha(0.2)
    for l in [violins['cbars'], violins['cmins'], violins['cmaxes']]:
        l.set_color((0.3, 0.3, 255 / 255, 1))
        l.set_linewidth(0.8)
    for x, y in zip([1, 2, 3, 4, 5, 6], [np.max(d) for d in data]):
        xy = (x + 0.15, y)
        va = 'center'
        if x == 1:
            xy = (x + 0.15, 62)
        if x == 3:
            xy = (x + 0.15, 62)
        if x == 4:
            xy = (x + 0.15, 62)
        if x == 5:
            xy = (x + 0.15, 62)
        if x == 6:
            xy = (x + 0.15, 62)
        plt.annotate(r"$n_{\mathrm{max}}="+f"{y: .2f}$", (x, y), xytext=xy,
                     arrowprops=arrowstyle if x != 2 else None, va=va)
    mean_hndl = plt.plot([1, 2, 3, 4, 5, 6], [np.mean(d)
                                     for d in data], 'x', color=(1, 0.1, 0.1, 1))
    for x, y in zip([1, 2, 3, 4, 5, 6], [np.mean(d) for d in data]):
        xy = (x + 0.15, y)
        if x == 1:
            xy = (x + 0.15, 42)
        if x == 2:
            xy = (x + 0.15, 42)
        if x == 3:
            xy = (x + 0.15, 42)
        if x == 4:
            xy = (x + 0.15, 42)
        if x == 5:
            xy = (x + 0.15, 42)
        if x == 6:
            xy = (x + 0.15, 42)
        plt.annotate(fr"$\bar{{n}}={y:.2f}$", (x, y), xytext=xy,
                     arrowprops=arrowstyle, va='center')
    median_hndl = plt.plot([1, 2, 3, 4, 5, 6], [np.median(d)
                                       for d in data], '_', color=(1, 0.55, 0.1, 1))
    for x, y in zip([1, 2, 3, 4, 5, 6], [np.median(d) for d in data]):
        xy = (x + 0.15, y)
        if x == 1:
            xy = (x + 0.15, 22)
        if x == 2:
            xy = (x + 0.15, 22)
        if x == 3:
            xy = (x + 0.15, 22)
        if x == 4:
            xy = (x + 0.15, 22)
        if x == 5:
            xy = (x + 0.15, 22)
        if x == 6:
            xy = (x + 0.15, 22)
        plt.annotate(fr"$\tilde{{n}}={y:.2f}$", (x, y), xytext=xy,
                     arrowprops=arrowstyle, va='center')
    for x, y in zip([1, 2, 3, 4, 5, 6], [np.min(d) for d in data]):
        #xy = (x + 0.15, y)
        #if x != 2:
        xy = (x + 0.15, 7)
        plt.annotate(r"$n_{\mathrm{min}}="+f"{y:.2f}$", (x, y), xytext=xy,
                     va='center')
    plt.xticks([1, 2, 3, 4, 5, 6], names)
    plt.yticks([0, 25, 50, 75, 100, 125, 150])
    plt.xlim(0.7, 6.75)
    plt.ylim(-5, 165)
    plt.tight_layout(pad=0)

    max_hndl = Line2D([0, 1], [0, 1], marker=3, color=(
        0.3, 0.3, 255 / 255, 1), linewidth=0.8)
    min_hndl = Line2D([0, 1], [0, 1], marker=2, color=(
        0.3, 0.3, 255 / 255, 1), linewidth=0.8)
    leg = plt.legend([max_hndl, mean_hndl[0], median_hndl[0], min_hndl],
                     [r'maximum $n_{\mathrm{max}}$', r'mean $\bar{n}$',
                      r'median $\tilde{n}$', r'minimum $n_{\mathrm{min}}$'],
                     loc='upper left', bbox_to_anchor=(0.02, 0.98), markerscale=0.6, handlelength=1.2, handletextpad=0.4, labelspacing=0.2, fancybox=False, borderpad=0.2)
    leg.get_frame().set_linewidth(0.4)
    plt.grid(axis='y', linewidth=0.4, color=(0.8, 0.8, 0.8, 1))

    plt.savefig("noise_level_dist.pdf")
    plt.show()
    plt.close()

def main():
    files = read_files(".")
    dataset = []
    for f in files:
        
        x_label = ""
        if "minife" in f:
            x_label = "MiniFE\n(Lichtenberg)"
        elif "lulesh" in f:
            x_label = "LULESH\n(Lichtenberg)"
        elif "kripke" in f:
            x_label = "Kripke\n(Vulcan)"
        elif "relearn" in f:
            x_label = "RELaARN\n(Lichtenberg)"
        elif "quicksilver" in f:
            x_label = "Quicksilver\n(Lichtenberg)"
        elif "fastest" in f:
            x_label = "FASTEST\n(SuperMUC)"
            
        x = (
            x_label,
            load_file(f)["noise"],
            load_file(f)["probability"]
            )
        
        dataset.append(x)
        
    #print(dataset)
    
    plot_noise(dataset)


if __name__ == "__main__":
    main()
    
