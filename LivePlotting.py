from IPython.display import clear_output
from matplotlib import pyplot as plt
import collections
import numpy as np
import time

def avg_diff_live_plot(*data_dicts,  figsize=(7,5), title='', xlabel = "Time (s)", ylabel="Power dB/m"):
    i = 0
    result = []
    avg_dict = {i:[] for i in range(len(data_dicts))}
    try:
        while True:
            clear_output(wait=True)
            plt.figure(figsize=figsize)
            colors=['blue','orange','green','purple','brown','pink','gray','olive','cyan','red']

            i = 0
            for data_dict in data_dicts:
                res = 0
                for val in data_dict.values(): 
                    res += val.measure()
                avg = res/len(data_dict)
                avg_dict[i].append(avg)
                i += 1
            result.append(avg_dict[0][-1] - avg_dict[1][-1])

            plt.plot(result, label= "Avg_Power")

            plt.title(title)
            plt.grid(True)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.legend(loc='center left') # the plot evolves to the right
            plt.show()
        
    except KeyboardInterrupt:
        print("Press Ctrl-C to terminate while statement")
        plt.plot(result, label= "Avg_Power")

        plt.title(title)
        plt.grid(True)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend(loc='center left') # the plot evolves to the right
        plt.show()
        

def avg_live_plot(*data_dicts,  figsize=(7,5), title='', xlabel = "Time (s)", ylabel="Power dB/m"):
    i = 0
    avg_dict = {i:[] for i in range(len(data_dicts))}
    try:
        while True:
            clear_output(wait=True)
            plt.figure(figsize=figsize)
            colors=['blue','orange','green','purple','brown','pink','gray','olive','cyan','red']

            i = 0
            for data_dict in data_dicts:
                res = 0
                for val in data_dict.values(): 
                    res += val.measure()
                avg = res/len(data_dict)
                avg_dict[i].append(avg)
                i += 1

            for label,data in avg_dict.items():
                plt.plot(data, label=label)

            plt.title(title)
            plt.grid(True)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.legend(loc='center left') # the plot evolves to the right
            plt.show()
    
    except KeyboardInterrupt:
        print("Press Ctrl-C to terminate while statement")
        for label,data in avg_dict.items():
            plt.plot(data, label=label)

        plt.title(title)
        plt.grid(True)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend(loc='center left') # the plot evolves to the right
        plt.show()


def live_plot(data_dict, figsize=(7,5), title='', xlabel = "Time (s)", ylabel="Power dB/m"):
    clear_output(wait=True)
    plt.figure(figsize=figsize)
    i=0
    #colors=['FireBrick','RoyalBlue','MediumVioletRed','Chocolate','DarkOrchid','Orchid','OliveDrab','LightSeaGreen','Gold','MediumSpringGreen']
    colors=['blue','orange','green','purple','brown','pink','gray','olive','cyan','red']
    for label,data in data_dict.items():
        plt.plot(data, label=label,color=colors[i])
        i+=1
    plt.title(title)
    plt.grid(True)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc='center left') # the plot evolves to the right
    plt.show()
    
def live_opt_pow(heaters):
    heater_data = {}
    plot_data={}
    for q in heaters.keys():
        heater_data[q] = []
        plot_data[q] = []
    try:
        while True:
            for i in heaters.keys():
                heater_data[i].append(heaters[i].measure())
                try:
                    plot_data[i] = heater_data[i][-100:]
                except:
                    plot_data[i] = heater_data[i]
            live_plot(plot_data)

    except KeyboardInterrupt:
        print("Press Ctrl-C to terminate while statement")
        live_plot(heater_data)
        
def Swabian_counts(channels, sleep_time = 1):
    counts_data = {}
    for q in channels.keys():
        counts_data[q] = []
    while True:
        for i in channels.keys():
            counts_data[i].append(channels[i].getData())
        live_plot(counts_data, xlabel = "Time", ylabel = "Counts/"+str(sleep_time)+"s")
        time.sleep(sleep_time)