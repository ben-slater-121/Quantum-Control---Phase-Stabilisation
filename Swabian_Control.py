

def set_trigger_levels(trigger_levels, tagger):
    for channels, threshold in trigger_levels.items():
        tagger.setTriggerLevel(channels, threshold)
        
def set_input_delays(input_delays, tagger):
    for channels, delay in input_delays.items():
        tagger.setInputDelay(channels, delay)
        
def Virutal_channel_creator(Num_of_Channels = 8):
    x = int(Num_of_Channels/2)
    x = x+1
    Coin_Combs = []
    for i in range(1,x):
        for j in range(5,4+x):
            if i != j:
                Coin_Combs.append([i,j])
            else:
                pass
    Coin_Combs
    return Coin_Combs

def Save_Coincidence_Counts(results):
    df_results = pd.DataFrame(results)
    path = df_results.to_csv("results/Counts_results_"+dt.now().strftime("%Y-%m-%d-%H-%M")+".csv", header = ["Channels", "Coincidence Counts"])
    return path 

def Plot_2D_results_4D(results):
    j = 1
    plotting_x = []
    plotting_y = []
    for i in results:
        plotting_x.append(str(i[0]))
        plotting_y.append(i[1])
        if j%4 == 0:
            plt.bar(plotting_x, plotting_y)
            plt.show()
            plotting_x = []
            plotting_y = []
        j +=1