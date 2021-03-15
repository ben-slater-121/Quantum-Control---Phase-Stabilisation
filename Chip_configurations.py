import numpy as np
pi=np.pi
# Identiy Chip Configuration

Idenity_3chips = {
    # Alice
    "BS1":pi/2,
    "BS2":pi/2,
    "BS3":pi/2,
    "WDM1":pi,
    "WDM2":pi,
    "WDM3":pi,
    "WDM4":pi,
    "Pre_RY1":pi,
    "Pre_RY2":pi,
    "Bell1":pi,
    "Bell2":pi,
    "Prj_RY1":pi,
    "Prj_RY2":pi,
    "Prj_RY3":pi,
    "Prj_RY4":pi,
    "Ctr_1":0,
    "Ctr_2":0,

    #Bob
    "Atta1":pi,
    "Atta2":pi,
    "Atta3":pi,
    "Atta4":pi,
    "MZIa1":pi,
    "MZIa2":pi,
    "MZIa3":pi,
    "MZIa4":pi,
    
    #Charlie
    "Attb1":pi,
    "Attb2":pi,
    "Attb3":pi,
    "Attb4":pi,
    "MZIb1":pi,
    "MZIb2":pi,
    "MZIb3":pi,
    "MZIb4":pi
    }

# Identiy ALICE Chip Configuration

Idenity_A_3chips = {
    # Alice
    "BS1":pi/2,
    "BS2":pi/2,
    "BS3":pi/2,
    "WDM1":pi,
    "WDM2":pi,
    "WDM3":pi,
    "WDM4":pi,
    "Pre_RY1":pi,
    "Pre_RY2":pi,
    "Bell1":pi,
    "Bell2":pi,
    "Prj_RY1":pi,
    "Prj_RY2":pi,
    "Prj_RY3":pi,
    "Prj_RY4":pi,
    "Ctr_1":0,
    "Ctr_2":0
    }

# Identiy Bob Chip Configuration

Idenity_B_3chips = {
    #Bob
    "Atta1":pi,
    "Atta2":pi,
    "Atta3":pi,
    "Atta4":pi,
    "MZIa1":pi,
    "MZIa2":pi,
    "MZIa3":pi,
    "MZIa4":pi,
    }

# Identiy Charlie Chip Configuration

Idenity_C_3chips = {
    #Charlie
    "Attb1":pi,
    "Attb2":pi,
    "Attb3":pi,
    "Attb4":pi,
    "MZIb1":pi,
    "MZIb2":pi,
    "MZIb3":pi,
    "MZIb4":pi
    }

Alice_FP_23 = {"BS1":pi/2,
    "BS2":pi,
    "BS3":pi,
    "WDM1":pi,
    "WDM2":pi,
    "WDM3":pi,
    "WDM4":pi,
    "Pre_RY1":pi,
    "Pre_RY2":pi,
    "Bell1":pi,
    "Bell2":pi,
    "Prj_RY1":pi,
    "Prj_RY2":pi,
    "Prj_RY3":pi,
    "Prj_RY4":pi,
    "Ctr_1":pi,
    "Ctr_2":pi,
    "Prj_RZ1":0,
    "Prj_RZ2":0,
    "Prj_RZ3":0,
    "Prj_RZ4":0,
    "Pre_RZ1":0,
    "Pre_RZ2":0,}

Bob_23_Had = {
    #Bob
    "Atta1":0,
    "Atta2":pi,
    "Atta3":pi,
    "Atta4":pi,
    "MZIa1":0,
    "MZIa2":pi,
    "MZIa3":pi/2,
    "MZIa4":pi
    ,
    }

Charlie_23_Had = {
    #Charlie
    "Attb1":0,
    "Attb2":pi,
    "Attb3":pi,
    "Attb4":0,
    "MZIb1":pi,
    "MZIb2":0,
    "MZIb3":pi,
    "MZIb4":pi/2
    }

Bob_23_Comp = {
    #Bob
    "Atta1":0,
    "Atta2":pi,
    "Atta3":pi,
    "Atta4":pi,
    "MZIa1":0,
    "MZIa2":pi,
    "MZIa3":pi,
    "MZIa4":pi
    ,
    }

Charlie_23_Comp = {
    #Charlie
    "Attb1":0,
    "Attb2":pi,
    "Attb3":pi,
    "Attb4":0,
    "MZIb1":pi,
    "MZIb2":0,
    "MZIb3":pi,
    "MZIb4":pi
    }