import numpy as np
from tunicsqontrol import tunics
from powermeter import Powermeter
# from swabian import TimeTaggerObject
from FirstLevel_Qontrol import HeaterQontrol
import matplotlib.pyplot as plt
from datetime import datetime
import os 
import time
import scipy.signal as s
import scipy.optimize as opt


class LockWavelength():

    '''Class to controll locking of rings to specific wavelengths'''

    def __init__(self,heaters,laser,powermeters,rings,v_array,wav_array,set_wavelengths,n_averages):
        

        if not isinstance(heaters, HeaterQontrol):
            raise Exception('heaters needs to be a FirstLevel_Qontrol.HeaterQontrol instance')
        if not isinstance(powermeters[0], Powermeter):
            raise Exception('powermeter needs to be a list of powermeter.Powermeter instances')
        if not isinstance(laser,tunics):
            raise Exception('laser needs to be a tunicsqontrol.tunics instance')


        self.heaters = heaters # heater control
        self.laser = laser # laser control
        self.powermeters = powermeters # list of poweremeters
        self.rings = rings # which rings to measure
        self.v_array = v_array # array of voltage arrays to sweep each ring
        self.wav_array = wav_array # wavelength array to check dip locations
        self.set_wavelengths = set_wavelengths #desired dip locations for the rings
        self.n_averages = n_averages 
        self.min_voltage_array = False
    def find_min_voltage(self,index,plot = True):
		
        '''Finds voltage that minimises the power transmitted by a single ring'''
        
        power_array = []
   
        if self.powermeters[index].measure() < -20: time.sleep(2)
        
        for voltage in self.v_array[index]:
            
            self.heaters.set_voltage(self.rings[index],voltage)
            time.sleep(0.2)
            
            power_array.append(self.powermeters[index].measure_average(self.n_averages))
        
        vis = max(power_array) - min(power_array)
        
        if vis < 1.2: print(f'Dip for {self.rings[index]} not found')
            
        min_voltage = self.v_array[index][np.argmin(power_array)]
        
        if plot:
            plt.figure()
            plt.plot(self.v_array[index],power_array)
            plt.show()
        
        return min_voltage


    def wavelength_sweep(self,plot=True):
    
        result_array = []
        
        for wavelength in self.wav_array:
            
            self.laser.laser_wavelength(wavelength)
            time.sleep(0.2)

            if any([powermeter.measure() < -20 for powermeter in self.powermeters]): time.sleep(2)
            power_temp = [powermeter.measure_average(self.n_averages) for powermeter in self.powermeters]
            
            result_array.append(power_temp)
   
        # results_array = np.array(result_array).T
    
        if plot:
            plt.figure() 
            [plt.plot(self.wav_array,power,'.') for power in np.array(result_array).T]
            plt.show()
       
        min_wavlength = [self.wav_array[np.argmin(result)] for result in np.array(result_array).T]
        print(min_wavlength)
      
        return min_wavlength,result_array

    def cost_function(self,v):

        if v[0] > 5:
            print('V1 too high1')
            res = 0
        elif v[1] > 5:
            print('V2 too high1')
            res = 0
        elif v[0] < 0:
            print('V1 negative')
            res = 0
        elif v[1] < 0:
            print('V2 negative')
            res = 0
        else:

            [self.heaters.set_voltage(ring,v[i]) for i,ring in enumerate(self.rings)]
            time.sleep(0.1)
            
            res = sum([powermeter.measure_average(2) for powermeter in self.powermeters])
   
        return res

    def get_starting_voltages(self,plot = True):
        
        '''Gets initial voltages - these are minimal voltages for each ring separately '''
        
        if isinstance(self.set_wavelengths,list): raise Exception('set_wavelengths should be one number. This functions assumes all rings to be locked to one wavelength.' )
        
        self.laser.laser_wavelength(self.set_wavelengths)
        self.laser.laser_power(9)
        self.laser.laser_switch(1)
        time.sleep(5)
        # print(f'Set wavelength = {self.laser.get_laser_wavelength()}')
        self.min_voltage_array = [self.find_min_voltage(i,plot=plot) for i in range(len(self.rings))]

        return 

    def optimise_voltages(self,options,method,threshold_lambda = 0.0022,diagnostics = False):

        '''Use nelder - mead optimisation to align multiple rings to the same wavelength - tested and working for 2 rings. '''

        if not self.min_voltage_array: raise Exception('Run get_starting_voltages to provide initial values for optimisation algorithm' )
        if isinstance(self.set_wavelengths,list): raise Exception('set_wavelengths should be one number. This functions assumes all rings to be locked to one wavelength.' )
        
        plot = False
        i = 0
        while True:
        	
        	
            self.laser.laser_wavelength(self.set_wavelengths)

            time.sleep(10)

            x0 = [np.random.normal(start_V,0.1) for start_V in self.min_voltage_array]

            print('Optimising')
            start_opti = time.time()
            res = opt.minimize(self.cost_function,x0,method = method,options = options)
            end_opti  = time.time()
            
            if diagnostics: 
                print(res)
                plot = True
                print(f'optimisation time = {end_opti - start_opti}')
            if res.success:
                
                [self.heaters.set_voltage(ring,res.x[i]) for i,ring in enumerate(self.rings)]
                time.sleep(0.2)
                print('sweep wavelength...')
                mins,powers = self.wavelength_sweep(plot=plot)
                if i == 10: break
                if diagnostics: 
                    print(mins) 
                    print(np.diff(mins))
                if abs(np.diff(mins)) < threshold_lambda and abs(mins[0] - self.set_wavelengths) < 0.02: break
            i += 1
        return res,mins,powers

    def lock_to_separate(self,plot=True):

        '''Find minimum voltages for different rings at different wavelengths - doesnt take into account crosstalk'''
        '''Needs testing'''
        if not isinstance(self.set_wavelengths,list): raise Exception('set_wavelengths should be a list.' )

        min_voltage_sep = []
        self.laser.laser_power(9)
        self.laser.laser_switch(1)
        for i,wavelength in enumerate(self.set_wavelengths):

            self.laser.laser_wavelength(wavelength)
            time.sleep(5)
            while self.powermeters[i].measure() < -20: time.sleep(1)

            min_voltage_sep.append(self.find_min_voltage(i,plot=plot))
        print(len(min_voltage_sep))
        [self.heaters.set_voltage(ring,voltage) for ring,voltage in zip(self.rings,min_voltage_sep)]
        mins,powers = self.wavelength_sweep(plot=plot)

        return min_voltage_sep