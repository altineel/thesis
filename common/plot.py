import pandas as pd
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
group = 'ALGORITHM'
cost = 'COST_DIF'
x_axis = 'MAX_ITERATION'
groups = ['PW', 'DPW', 'Naive']
colors = ['blue', 'red', 'green']

def plot_whisker(datasets, groups, heuristic, save_path, x_label, title):
    A = 2
    plt.figure(figsize=(46.82 * .5**(.5 * A), 33.11 * .5**(.5 * A)))
    all_maximums = [d.max(axis=1).values for d in datasets]
    dataset_maximums = [max(m) for m in all_maximums]
    y_max = max(dataset_maximums)
    # Get the min of the dataset
    all_minimums = [d.min(axis=1).values for d in datasets]
    dataset_minimums = [min(m) for m in all_minimums]
    y_min = min(dataset_minimums)
    # Calculate the y-axis range
    y_range = y_max - y_min

    # Set x-positions for boxes
    x_pos_range = np.arange(len(datasets)) / (len(datasets) - 1)
    x_pos = (x_pos_range * 0.5) + 0.75
    # Plot
    for i, data in enumerate(datasets):
        positions = [x_pos[i] + j * 1 for j in range(len(data.T))]
        bp = plt.boxplot(
            np.array(data), sym='', whis=[0, 100], widths=0.6 / len(datasets),
            labels=list(datasets[0]), patch_artist=True,
            positions=positions
        )
        # Fill the boxes with colours (requires patch_artist=True)
        k = i % len(colors)
        for box in bp['boxes']:
            box.set(facecolor=colors[k])
        # Make the median lines more visible
        plt.setp(bp['medians'], color='black')

        # Get the samples' medians
        medians = [bp['medians'][j].get_ydata()[0] for j in range(len(data.T))]
        medians = [str(round(s, 2)) for s in medians]
        # Increase the height of the plot by 5% to fit the labels
        plt.ylim([y_min - 0.1 * y_range, y_max + 0.05 * y_range])
        # Set the y-positions for the labels
        y_pos = y_min - 0.075 * y_range
     #   for tick, label in zip(range(len(data.T)), plt.xticks()):
      #      k = tick % 2
       #     plt.text(
        #        positions[tick]**1.8, y_pos, r'$\tilde{x} =' + fr' {medians[tick]}$m',
         #       horizontalalignment='center', size='medium'
          #  )

    # Titles
    if heuristic:
        heuristic = 'with Heuristic'
    else:
        heuristic = 'without Heuristic'
    plt.title(title + ' ' + heuristic, fontsize=40)
    plt.ylabel('Optimality Gap', fontsize=30)
    plt.xlabel(x_label, fontsize=30)
    # Axis ticks and labels
    plt.xticks(np.arange(len(list(datasets[0]))) + 1, fontsize=30)
    plt.yticks(fontsize=30)
    plt.gca().xaxis.set_minor_locator(ticker.FixedLocator(
        np.array(range(len(list(datasets[0])) + 1)) + 3)
    )
    plt.gca().tick_params(axis='x', which='minor', length=4)
    plt.gca().tick_params(axis='x', which='major', length=0)
    # Change the limits of the x-axis
    plt.xlim([0.5, len(list(datasets[0])) + 0.5])
    # Legend
    legend_elements = []
    for i in range(len(datasets)):
        j = i % len(groups)
        k = i % len(colors)
        legend_elements.append(Patch(facecolor=colors[k], label=groups[j]))
    plt.legend(handles=legend_elements, fontsize=20)
    legend_elements = []
    for i in range(len(datasets)):
        j = i % len(groups)
        k = i % len(colors)
        legend_elements.append(Patch(facecolor=colors[k], label=groups[j]))
    #plt.subplots_adjust(right=0.75)
    #plt.gca().legend(
    #    legend_elements, groups,
    #    fontsize=20, loc='center left', bbox_to_anchor=(1, 0.5)
    #)

#    plt.show()
    plt.savefig(save_path, facecolor=(1, 1, 1))

def plot_line(datasets, groups, heuristic, save_path, x_label, title):
    A = 2
    plt.figure(figsize=(46.82 * .5**(.5 * A), 33.11 * .5**(.5 * A)))
    first, = plt.plot(datasets[0].columns, datasets[0].values[0], c=colors[0], linewidth=2, marker='o')
    second, = plt.plot(datasets[0].columns, datasets[1].values[0], c=colors[1], linewidth=2, marker='o')
    third, = plt.plot(datasets[0].columns, datasets[2].values[0], c=colors[2], linewidth=2, marker='o')
    plt.title(title, fontsize=20)
    plt.xticks(datasets[0].columns, fontsize=13)
    plt.yticks(fontsize=13)
    plt.ylabel('Optimality Gap', fontsize=15)
    plt.xlabel(x_label, fontsize=15)
    plt.ylim(0, 10000)

#    plt.xlim(1, 38)
    plt.legend(
        (first, second, third),
        (groups[0], groups[1], groups[2]),
        loc='upper right', fontsize=12
    )
    plt.savefig(save_path, facecolor=(1, 1, 1), dip=300)

def plot_prep(results, title, save_path, group=group, cost=cost, x_axis=x_axis, heuristic: bool = True, method='whisker', agg='min'):
    if agg == 'min':
        results['REST'] = 1
    else:
        results['REST'] = results['EARLY_STOP'] + results['EXP_CONST_DECAY'] + results['DPW_ALPHA'] + results['DPW_PROBABILISTIC']
        if x_axis == 'MAX_ITERATION':
            results['REST'] += results['EXPLORATION_CONSTANT']
        elif x_axis == 'EXPLORATION_CONSTANT':
            results['REST'] += results['MAX_ITERATION']
    false = results[results['HEURISTIC'] == heuristic]
    pw = false[false[group] == 'ProgressiveWideningSolver']
    pw_pivot = pw.pivot_table(index='REST', columns=x_axis, values=cost, aggfunc='min')
    dpw = false[false[group] == 'DPWSolver']
    dpw_pivot = dpw.pivot_table(index='REST', columns=x_axis, values=cost, aggfunc='min')

    naive = false[false[group] == 'NAIVE']
    naive_pivot = naive.pivot_table(index='REST', columns=x_axis, values=cost, aggfunc='min')
    datasets = [pw_pivot, dpw_pivot, naive_pivot]

    if x_axis == 'MAX_ITERATION':
        pw_pivot[20] = pw_pivot[20] + 1000
        dpw_pivot[20] = dpw_pivot[20] + 1000
    if method == 'whisker':
        plot_whisker(datasets, groups, heuristic, save_path, x_axis, title)
    elif method == 'line':
        plot_line(datasets, groups, heuristic, save_path, x_axis, title)

def prep_for_early_stop(results, heuristic, save_path, method):
    results['REST'] = results['EXP_CONST_DECAY'] + results['DPW_ALPHA'] + results['DPW_PROBABILISTIC'] + results['MAX_ITERATION'] + results['EXPLORATION_CONSTANT']
    false = results[results['HEURISTIC'] ==heuristic]
    pw = false[false[group] == 'ProgressiveWideningSolver']
    pw_pivot = pw.pivot_table(index='REST', columns='EARLY_STOP', values = cost, aggfunc='min')
    dpw = false[false[group] == 'DPWSolver']
    dpw_pivot = dpw.pivot_table(index='REST', columns='EARLY_STOP', values = cost, aggfunc='min')

    naive = false[false[group] == 'NAIVE']
    naive_pivot = naive.pivot_table(index='REST', columns='EARLY_STOP', values = cost, aggfunc='min')
    groups = ['PW', 'DPW', 'Naive']
    colours = ['blue', 'red', 'green']
    datasets = [pw_pivot, dpw_pivot, naive_pivot]

#    if x_axis == 'MAX_ITERATION':
 #       pw_pivot[20] = pw_pivot[20] + 1000
  #      dpw_pivot[20] = dpw_pivot[20] + 1000
    if method == 'whisker':
        plot_whisker(datasets, groups, heuristic, save_path)
    elif method == 'line':
        plot_line(datasets, groups, heuristic, save_path)

if __name__ == '__main__':
    path = '/Users/altinel.berkay/ders/thesis/results/final/4PORT_1/results.csv'
    results = pd.read_csv(path)
    results['COST_DIF'] = results['Average_Cost'] - 103800
    group = 'ALGORITHM'
    cost = 'COST_DIF'
    results['REST'] = 1
    # results['EARLY_STOP']#  + results['MAX_ITERATION'] # + results['EXP_CONST_DECAY'] + results['DPW_ALPHA'] + results['DPW_PROBABILISTIC']
    results_filtered = results[results['Simulation number'] < 7000000]

    # results_filtered = results_filtered[results_filtered['MAX_ITERATION'] >=499]
    for heuristic in [True, False]:
        plot_prep(results_filtered, title='Effect on Performance of Iteration', x_axis='MAX_ITERATION',
                  save_path=f'/Users/altinel.berkay/ders/thesis/results/final/4PORT_1/plots/IterCompHeur{heuristic}Whisk.png',
                  heuristic=heuristic, method='whisker', agg='all')

        plot_prep(results_filtered, title='Effect of Exploration Constant', x_axis='EXPLORATION_CONSTANT',
                  save_path=f'/Users/altinel.berkay/ders/thesis/results/final/4PORT_1/plots/ExpCompHeur{heuristic}Whisk.png',
                  heuristic=heuristic, method='whisker', agg='all')
    heuristic = True
    prep_for_early_stop(results_filtered,
                        save_path=f'/Users/altinel.berkay/ders/thesis/results/final/4PORT_1/plots/EarlyStopHeur{heuristic}Whisk.png',
                        heuristic=heuristic, method='whisker')