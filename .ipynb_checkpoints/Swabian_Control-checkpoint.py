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