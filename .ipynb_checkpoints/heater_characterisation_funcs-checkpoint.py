import numpy as np 
from FirstLevel_Qontrol import HeaterQontrol
from SecondLevel_Qontrol import heater_class
from powermeter import Powermeter
import time
from scipy import optimize
import matplotlib.pyplot as plt 

def dB_to_power(dBs):
    """
    converts dB to power
    """
    return 10.**(0.1*dBs)
    
def get_all_working_channels(heaters, current_threshold=0.05):
    """
    tries to set v=1 to all channels and then measures the currnent 
    If a current larger than current_threshold flows, then we assume channel is working

    returns a dict of channels which were above thresholds and their assosciated currents
    """
    #if not isinstance(heaters, HeaterQontrol):
    #    raise Exception('first arg needs to be instance of FirstLevel_Qontrol.HeaterQontrol')
    working_channels = dict()
    for channel in range(heaters.n_chs):
        heaters.set_all_zeros()
        heaters.q.v[channel] = 1
        time.sleep(0.1)
        current = heaters.q.i[channel]
        if current > current_threshold:
            working_channels[channel] = current
    heaters.set_all_zeros()
    return working_channels

def measure_fringe(heaters, pwrmtr, heater_name, v_max, steps, sleep_time=0.2):
    """
    sweeps voltage from zero to voltage_max and measures the power of the pwrmtr

    returns np.arrays of voltage and power so you can plot a fringe 
    """
    #if not isinstance(heaters, HeaterQontrol):
    #    raise Exception('first arg needs to be instance of FirstLevel_Qontrol.HeaterQontrol')
    if not isinstance(pwrmtr, Powermeter):
        raise Exception('second arg needs to be instance of Powermeter.powermeter')
    voltages = np.linspace(0,v_max,steps)
    powers = []
    for v in voltages:
        heaters.set_voltage(heater_name=heater_name, voltage=float(v))
        time.sleep(sleep_time)
        powers.append(pwrmtr.measure())
    heaters.set_all_zeros()
    return voltages, np.array(powers)

def measure_v_i_curve(h, heater_name, v_max, steps, sleep_time=0.1):
    """
    sweeps voltage from 0 to v_max and measures the current at each step

    returns np.arrays of voltage and current for extracting the resistance
    """
    #if not isinstance(heaters, heater_class):
    #    raise Exception('first arg needs to be instance of FirstLevel_Qontrol.HeaterQontrol')
    voltages = np.linspace(0, v_max, steps)
    currents = []
    for v in voltages:
        h.set_voltage(heater_name, float(v))
        time.sleep(sleep_time)
        currents.append(h.read_current(heater_name))
    h.set_all_zeros_bad()
    return voltages, np.array(currents)

def measure_fringe_and_v_i(h, pwrmtr, heater_name, v_max, steps, sleep_time=0.2, shuffle_order=False):
    """
    sweeps voltage from zero to voltage_max and measures the power of the pwrmtr

    returns np.arrays of voltage and power so you can plot a fringe 
    """
    #if not isinstance(heaters, heater_class):
    #    raise Exception('first arg needs to be instance of FirstLevel_Qontrol.HeaterQontrol')
    if not isinstance(pwrmtr, Powermeter):
        raise Exception('second arg needs to be instance of Powermeter.powermeter')
    voltages = np.sqrt(np.linspace(0,v_max**2,steps))   #quadratically spaced array
    if shuffle_order:
        np.random.shuffle(voltages)
    powers = []
    currents = []
    for v in voltages:
        h.set_voltage(heater_name=heater_name, voltage=float(v))
        time.sleep(sleep_time)
        powers.append(pwrmtr.measure())
        currents.append(h.read_current(heater_name))
    h.set_all_zeros_bad()
    return voltages, np.array(powers), np.array(currents)

def _save_fit_params(heater_name, alpha, beta, gamma, c, phi_0, phase_offset):
    #rewrite the current fit params file
    with open(f'C:/Users/bs15598/University of Bristol/grp-Multi 3 Chip Project - Documents/Multi_3_Chips/pycode_molly/Experimental code/Experimental data/Calibration/Heaters/{heater_name}.csv', 'w') as file:
    #with open(f'../Experimental data/Calibration/Heaters/{heater_name}.csv', 'w') as file:
        file.write('# alpha, beta, gamma, c, phi_0, phase_offset\n')
        file.write(f'{alpha},{beta},{gamma},{c},{phi_0%(2*np.pi)},{phase_offset%(2*np.pi)}')
    #add the new fit params with a timestamp to the archive of fit params
    #with open(f'../Experimental data/Calibration/Heaters/Old Calibration/{heater_name}_{int(time.time())}.csv', 'w') as file:
    #    file.write('# alpha, beta, gamma, c, phi_0 \n')
    #    file.write(f'{alpha},{beta},{gamma},{c},{phi_0%(2*np.pi)}')

def _save_fringes(heater_name, voltages, powers_mW):
    saving_array = np.vstack((voltages, powers_mW)).T
    np.savetxt(f'C:/Users/bs15598/University of Bristol/grp-Multi 3 Chip Project - Documents/Multi_3_Chips/pycode_molly/Experimental code/Experimental data/Calibration/Fringes/{heater_name}_{int(time.time())}.csv', saving_array,
        delimiter=',', header='#voltages,powers_mW')

def mzi_fringe_curve(v, c, phi_0, alpha, beta, gamma, A, B):
    P = alpha * v ** 3 + beta * v ** 2 + gamma * v
    return A*np.sin(c*P + phi_0)**2 + B

def characterise_heater(h,
    pwrmtr,
    heater_name,
    all_other_heater_phases,
    phase_offset,
    v_max,
    steps=20,
    sleep=0.2,
    chunk_size=4,
    fringe_fit_guess=[],
    plot=True,
    shuffle_order=False,
    infer_ab_from_data=True):
    """
    function carries out the following:
    measures an i/v curve and fits with 2nd order polynomial
    measures and fits fringe while sweeping phase
    saves data

    returns voltages_i, currents, alpha, beta, gamma, voltages_p, powers_mW, c, phi_0
    """
    #if not isinstance(heaters, heater_class):
    #    raise Exception('first arg needs to be instance of FirstLevel_Qontrol.HeaterQontrol')
    #if not isinstance(pwrmtr, Powermeter):
    #    raise Exception('second arg needs to be instance of powermeter.Powermeter')

    h.set_all_zeros_bad()
    h.set_many_phases(all_other_heater_phases, chunk_size)
    time.sleep(sleep)
    voltages, powers_mdB, currents = measure_fringe_and_v_i(h, pwrmtr, heater_name, v_max, steps, sleep, shuffle_order=shuffle_order)

    if shuffle_order:
        powers_mdB = np.array([i for _,i in sorted(zip(voltages, powers_mdB))])
        currents = np.array([i for _,i in sorted(zip(voltages, currents))])
        voltages.sort()
    alpha, beta, gamma = np.polyfit(voltages, currents, 2) #2nd order polynomial fit I = gamma + beta * V + alpha * V ** 2
    powers_mW = dB_to_power(powers_mdB)

    if infer_ab_from_data:
        p_min, p_max = powers_mW.min(), powers_mW.max()
        a = 0.5*(p_max - p_min)
        b = 0.5*(p_min + p_max)
        fringe_fit_guess = fringe_fit_guess[:2] + [a, b]
        
    def _mzi_fringe_curve(v, c, phi_0, A, B):
        P = alpha * v ** 3 + beta * v ** 2 + gamma * v
        return A*np.sin(c*P + phi_0)**2 + B
    try:
        lower_bounds = -np.inf
        upper_bounds = np.inf
        (c, phi_0, A, B), pcov = optimize.curve_fit(_mzi_fringe_curve, voltages, powers_mW, p0=fringe_fit_guess, bounds=(lower_bounds, upper_bounds))
    except:
        print('fitting failed')
        (c, phi_0, A, B) = (0,0,0,0)

    print(c, phi_0, A, B)
    h.set_all_zeros_bad()

    def voltage_to_phase(v):
        P = alpha * v ** 3 + beta * v ** 2 + gamma * v 
        return (2*c * P + (2*phi_0-phase_offset)) % (2 * np.pi)

    _save_fit_params(heater_name, alpha, beta, gamma, c, phi_0, phase_offset)
    #save_fringes(heater_name, voltages, powers_mW)

    #_save_fringes('power', alpha * voltages ** 3 + beta * voltages ** 2 + gamma * voltages, powers_mW)
    #_save_fringes('voltages', voltages, powers_mW)
    #_save_fringes('IV_curve', voltages, alpha * voltages ** 2 + beta * voltages + gamma)
    
    
    if plot:
        fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(6.4,10))
        ax1.plot(voltages, currents, '+', label='data', markersize=8)
        ax1.plot(voltages, alpha * voltages**2 + beta * voltages + gamma, label='fit')
        ax1.set_xlabel('V')
        ax1.set_ylabel('I')
        ax1.legend()
        ax2.plot(alpha * voltages ** 3 + beta * voltages ** 2 + gamma * voltages, powers_mW, '+', label='data', markersize=8)#**2
        ax2.plot(alpha * voltages ** 3 + beta * voltages ** 2 + gamma * voltages, mzi_fringe_curve(voltages, c, phi_0, alpha, beta, gamma, A, B), label='fit')
        ax2.set_xlabel(r'$V^2$')
        ax2.set_ylabel('Power (mW)')
        ax2.legend()
        ax3.plot(voltage_to_phase(voltages), powers_mW, 'o')#voltage_to_phase(voltages)
        ax3.set_xlabel('Phase')
        ax3.set_ylabel('Power (mW)')
        plt.tight_layout()
    return voltages, currents, alpha, beta, gamma, powers_mW, c, phi_0, A, B

def plot_phase_fringe(heaters, pwrmtr, heater_name, steps=50):
    phases = np.linspace(0, 2*np.pi)
    powers_mdB = []
    for phase in phases:
        heaters.set_phase(heater_name, phase)
        powers_mdB.append((pwrmtr.measure()))
        time.sleep(0.1)
    heaters.set_all_zeros()
    plt.figure()
    plt.plot(phases, dB_to_power(np.array(powers_mdB)))

def heater_cooking(heaters, voltage, total_time, recording_interval):
    heaters.set_all_zeros()
    heater_names = list(heaters.heater_dict.keys())
    for gnd_name in ['GND0A', 'GND1A', 'GND2A', 'GND0B', 'GND1B', 'GND2B']:
        heater_names.remove(gnd_name)
    heaters.set_many_voltages({name : voltage for name in heater_names})
    start_time = time.time()
    current_time = start_time
    all_currents = dict()
    while current_time - start_time < total_time:
        time.sleep(recording_interval)
        current_time = time.time()
        currents = heaters.read_many_currents(heater_names)
        all_currents[current_time-start_time] = currents
    heaters.set_all_zeros()
    return all_currents

def amzi_singles_fringe(heaters, tagger, heater_name, other_phases, channel, steps, sleep, integration_time, delay=0, trigger=[0.15]):
    heaters.set_all_zeros()
    heaters.set_many_phases(other_phases)
    dt = 1e-5 * integration_time
    binwidth = 1e-5 * 1e12 * integration_time
    delay_hardware = 1e9

    amzi_phases = np.linspace(0,2*np.pi,steps)
    counts = np.zeros(steps)
    for i, phase in enumerate(amzi_phases):
        heaters.set_phase(heater_name, phase)
        time.sleep(sleep)
        count_index, count_data = tagger.get_singles(channels=[channel],
                                                    binwidth=binwidth,
                                                    integration_time=integration_time,
                                                    channel_settings=[channel],
                                                    delay=[delay],
                                                    trigger=trigger,
                                                    dt=dt,
                                                    delay_Hardware=delay_hardware)
        counts[i] = np.sum(count_data[0])
    heaters.set_all_zeros()
    return amzi_phases, counts