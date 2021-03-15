import numpy as np 
import matplotlib.pyplot as plt
import time
import LivePlotting as LP
import Swabian_Control as SC
import collections
from tqdm import tqdm
import TimeTagger as TT

import pandas as pd
from datetime import datetime as dt
from qutip import *

pi=np.pi

save_path = "results/Counts_results_"
tagger = TT.createTimeTagger()