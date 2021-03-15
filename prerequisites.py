import numpy as np 
import matplotlib.pyplot as plt
import time
import ZeroLevel_Qontrol as q0
import FirstLevel_Qontrol as q1
import SecondLevel_Qontrol as q2
from powermeter import Powermeter as PM
import heater_dict as hd
import heater_characterisation_funcs as hcf
from tunicsqontrol import tunics
import LivePlotting as LP
import Swabian_Control as SC
import collections
from tqdm import tqdm
import TimeTagger as TT
import Useful_Functions as UF
import Chip_configurations as CF
from lock_wavelengths import LockWavelength as lw
import csv
import pandas as pd
from scipy import optimize
#import phase_stab as ps

pi=np.pi

"""serial_port_name_qontrol = 'COM3'
q = q0.QXOutput(serial_port_name=serial_port_name_qontrol, response_timeout=0.1)
heaters = q1.HeaterQontrol(q, uep.heater_dict, default_max_v=7)"""
h=q2.heater_class(hd.board_list,hd.heaters)

from common_chip_settings import *
