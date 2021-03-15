import numpy as np
#definitions: [board,port,max voltage,max phase]
CommonLimitV = 3.5
board_list=["COM9","COM7","COM11"]
heaters = {}
#heater board 1:
heaters["b_Ctr2"]=[0,0,4.0,2*np.pi]
heaters["b_Ctr1"]=[0,1,4.0,2*np.pi]
heaters["Yb"]=[0,2,4.0,2*np.pi]
heaters["Zb"]=[0,3,5.2,2*np.pi]
heaters["Yb8"]=[0,11,CommonLimitV,2*np.pi]
heaters["Yb7"]=[0,12,CommonLimitV,2*np.pi]
heaters["Zb16"]=[0,13,CommonLimitV,2*np.pi]
heaters["Zb15"]=[0,14,CommonLimitV,2*np.pi]
heaters["Prj_RY3"]=[0,15,3.5,2*np.pi]
heaters["Prj_RZ3"]=[0,16,3.5,2*np.pi]
heaters["Ctr_1"]=[0,17,3.5,2*np.pi]
heaters["Ctr_2"]=[0,18,3.8,2*np.pi]
heaters["Bell2"]=[0,19,4.0,2*np.pi]
heaters["Pre_RZ2"]=[0,20,3.5,2*np.pi]
heaters["Prj_RY4"]=[0,21,4.8,2*np.pi]
heaters["Pre_RY2"]=[0,22,4.0,2*np.pi]
heaters["WDM4"]=[0,23,3.5,2*np.pi]
heaters["Prj_RZ4"]=[0,24,3.8,2*np.pi]
heaters["MRR4"]=[0,25,CommonLimitV,2*np.pi]
heaters["BS3"]=[0,26,4.1,2*np.pi]
heaters["MRR3"]=[0,27,4.0,2*np.pi]
heaters["WDM3"]=[0,28,4.0,2*np.pi]
heaters["BS1"]=[0,29,4.0,2*np.pi]
heaters["WDM2"]=[0,30,3.5,2*np.pi]
heaters["MRR2"]=[0,31,CommonLimitV,2*np.pi]
heaters["BS2"]=[0,32,4.0,2*np.pi]
heaters["MRR1"]=[0,33,CommonLimitV,2*np.pi]
heaters["Prj_RZ1"]=[0,34,3.6,2*np.pi]
heaters["WDM1"]=[0,35,3.5,2*np.pi]
heaters["Pre_RY1"]=[0,36,3.7,2*np.pi]
heaters["Prj_RY1"]=[0,37,3.5,2*np.pi]
heaters["Pre_RZ1"]=[0,38,3.5,2*np.pi]
heaters["Bell1"]=[0,39,3.5,2*np.pi]
heaters["Prj_RZ2"]=[0,40,4.0,2*np.pi]
heaters["Prj_RY2"]=[0,41,3.7,2*np.pi]
#heater board 2:
heaters["Pha3"]=[1,0,CommonLimitV,2*np.pi]
heaters["Pha4"]=[1,1,CommonLimitV,2*np.pi]
heaters["Atta3"]=[1,2,CommonLimitV,2*np.pi]
heaters["Atta4"]=[1,3,CommonLimitV,2*np.pi]
heaters["MZIa2"]=[1,4,CommonLimitV,2*np.pi]
heaters["Pha6"]=[1,5,CommonLimitV,2*np.pi]
heaters["MZIa4"]=[1,6,CommonLimitV,2*np.pi]
heaters["Pha2"]=[1,8,CommonLimitV,2*np.pi]
heaters["Pha1"]=[1,9,3.5,2*np.pi]
heaters["Atta2"]=[1,10,3.5,2*np.pi]
heaters["Atta1"]=[1,11,CommonLimitV,2*np.pi]
heaters["MZIa1"]=[1,12,3.5,2*np.pi]
heaters["Pha5"]=[1,13,4.0,2*np.pi]
heaters["MZIa3"]=[1,14,CommonLimitV,2*np.pi]
#heater board 3:
heaters["MZIb3"]=[2,0,CommonLimitV,2*np.pi]
heaters["Phb5"]=[2,1,3.5,2*np.pi]
heaters["MZIb1"]=[2,2,3.5,2*np.pi]
heaters["Attb1"]=[2,3,CommonLimitV,2*np.pi]
heaters["Attb2"]=[2,4,CommonLimitV,2*np.pi]
heaters["Phb1"]=[2,5,CommonLimitV,2*np.pi]
heaters["Phb2"]=[2,6,CommonLimitV,2*np.pi]
heaters["Phb3"]=[2,7,CommonLimitV,2*np.pi]
heaters["Phb4"]=[2,8,CommonLimitV,2*np.pi]
heaters["Attb3"]=[2,9,CommonLimitV,2*np.pi]
heaters["Attb4"]=[2,10,CommonLimitV,2*np.pi]
heaters["MZIb2"]=[2,11,CommonLimitV,2*np.pi]
heaters["Phb6"]=[2,12,CommonLimitV,2*np.pi]
heaters["MZIb4"]=[2,13,CommonLimitV,2*np.pi]

"""def HeaterParams(heater_name):
    heater_board=heaters.get(heater_name)[0]
    heater_port=heaters.get(heater_name)[1]
    heater_limit=heaters.get(heater_name)[2]"""
    
max_voltages={name: heaters.get(name)[2] for name in heaters.keys()}

#print(max_voltage)

#print(max_voltages)
import serial
import pyvisa