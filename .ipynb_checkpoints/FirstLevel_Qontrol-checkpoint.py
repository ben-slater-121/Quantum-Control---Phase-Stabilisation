import ZeroLevel_Qontrol as qontrol
import numpy as np 
import time


def phase_to_voltage(heater_name, phase):
    #load heater parameters
    alpha, beta, gamma, c, phi_0, phase_offset= np.loadtxt(f'C:/Users/bs15598/University of Bristol/grp-Multi 3 Chip Project - Documents/Multi_3_Chips/pycode_molly/Experimental code/Experimental data/Calibration/Heaters/{heater_name}.csv', delimiter=',')

    #invert function
    a0 = -((phase - 2*phi_0 - phase_offset) % (2 * np.pi)) / (2*c * alpha) 
    a1 = gamma / alpha
    a2 = beta / alpha
    q = ((1./3.) * a1) - (1./9.) * (a2 ** 2)
    r = (1./6.) * (a1 * a2 - 3 * a0) - (1./27.) * (a2 ** 3)

    s1 = (r + np.sqrt(q ** 3 + r ** 2 + 0j))**(1./3.)
    s2 = (r - np.sqrt(q ** 3 + r ** 2 + 0j))**(1./3.)

    solutions = [
        (s1 + s2) - (a2 / 3),
        -0.5 * (s1 + s2) - (a2 / 3) + 0.5j * np.sqrt(3) * (s1 - s2),
        -0.5 * (s1 + s2) - (a2 / 3) - 0.5j * np.sqrt(3) * (s1 - s2)
        ]

    real_positive_solutions = []
    for s in solutions:
        if s.real == abs(s):
            real_positive_solutions.append(s.real)

    return min(real_positive_solutions)

def _iterable_to_vecstring(my_iter):
    """
    converts any iterable to a string with format 'a,b,c,d'
    so that it can be given to the vvec command
    """
    return ','.join(str(i) for i in my_iter)

class HeaterQontrol():
    """
    Class containing the first level functions for controlling the heaters

    q is the qontrol QXOutput class for the experiment
    heater_dict is a dictionary which maps heater names to their electronics channel number
    """
    def __init__(self, q, heater_dict, max_voltages=None, default_max_v=3):
        if not isinstance(q, qontrol.QXOutput):
            raise Exception('first arg needs to be a ZeroLevel_Qontrol.QXOutput instance')
        self.q = q
        self.heater_dict = heater_dict
        #max voltages dict to keep track of what we are willing to set each heater to
        if max_voltages is None:
            self.max_voltages = {name : default_max_v for name in heater_dict.keys()}
        else:
            self.max_voltages = max_voltages
        self.n_chs = q.n_chs

        self.set_all_zeros()
        self.voltages_array = np.zeros(self.n_chs)

    def _set_vect(self, start_ch, voltage_array):
        """
        set vector command, seems to only like setting 8 at a time for some reason
        start_ch : first channel of array to be set
        voltage_array : iterable array of ints or floats to be set to sequence of channels from start_ch
        """
        self.q.issue_command(command_id='vvec',
            ch=start_ch,
            operator='=',
            value=_iterable_to_vecstring(voltage_array))

    def set_all_zeros(self):
        """sets all voltages to zero"""
        self.q.issue_command(command_id='vall', operator='=', value=0)  

    def set_all_voltages(self, v):
        """sets all voltages to v"""
        if min(self.max_voltages.values()) > v:
            self.q.issue_command(command_id='vall', operator='=', value=v)
        else:
            print('voltage too high, was not set')
        
    def set_voltage(self, heater_name, voltage):
        """
        set voltages one at a time
        heater_name : string which labels the channel
        voltage : voltage value to be set (int or float)
        """
        if self.max_voltages[heater_name] >= voltage:
            channel = self.heater_dict.get(heater_name)
            if channel is not None:
                self.q.v[channel] = float(voltage)
                self.voltages_array[channel] = voltage
            else:
                print(f'{heater_name} is not in the heater dict, no voltage was set')
        else:
            print(f'voltage for {heater_name} was too high, so was not set')
            print(f'tried to set {voltage} but max is {self.max_voltages[heater_name]}')

    def set_many_voltages(self, names_voltages_dict, chunk_size=4, sleep_time=0.02):
        """
        sets many voltages at a time

        temporarily this just repeatidly calls set_voltage

        when fixed:

        Calls vvec in chunks of size chunks_size to speed up communications time
        names_voltages_dict is a dict which contains heater_names keys and voltage values to be set
        """
        # channels = []
        # new_voltages_array = self.voltages_array.copy()
        # for heater_name, voltage in names_voltages_dict.items():
        #     if self.max_voltages[heater_name] >= voltage:
        #         channel = self.heater_dict.get(heater_name)
        #         if channel is not None:
        #             channels.append(channel)
        #             new_voltages_array[channel] = voltage
        #         else:
        #             print(f'{heater_name} is not in the heater dict, no voltage will get set')
        #     else:
        #         print(f'voltage for {heater_name} was too high, so was not set')
        #         print(f'tried to set {voltage} but max is {self.max_voltages[heater_name]}')
        # if channels:
        #     for chunk in range(min(channels), max(channels)+1, chunk_size):
        #         new_voltages_chunk = new_voltages_array[chunk : chunk+chunk_size]
        #         if not np.array_equal(self.voltages_array[chunk : chunk+chunk_size], new_voltages_chunk):
        #             self._set_vect(chunk, new_voltages_chunk)
        for name, voltage in names_voltages_dict.items():
            self.set_voltage(name, voltage)
            time.sleep(sleep_time)

    def set_phase(self, heater_name, phase):
        """
        set phase one at a time
        heater_name : string which labels the channel
        phase : phase value to be set (int or float)
        """
        v = phase_to_voltage(heater_name, phase)
        self.set_voltage(heater_name, v)

    def set_many_phases(self, names_phases_dict, chunk_size=4):
        """
        sets many phases at a time
        Calls vvec in chunks of size chunks_size to speed up communications time
        names_phases_dict is a dict which contains heater_names keys and phase values to be set     
        """
        names_voltages_dict = {name : phase_to_voltage(name, phase) for name, phase in names_phases_dict.items()}
        self.set_many_voltages(names_voltages_dict, chunk_size)

    def read_voltage(self, heater_name):
        """
        read channel a single voltage
        heater_name : string which labels the channel
        returns a float of the voltage
        """
        channel = self.heater_dict.get(heater_name)
        if channel is not None:
            return self.q.v[channel]
        else:
            print(f'{heater_name} is not in the heater dict, cannot read voltage')

    def read_many_voltages(self, heater_names):
        """
        read multiple voltages
        heater_names : iterable of heaters to be read
        returns dict of names : voltage pairs
        """
        voltages = dict()
        for heater_name in heater_names:
            channel = self.heater_dict.get(heater_name)
            if channel is not None:
                voltages[heater_name] = self.q.v[channel]
            else:
                print(f'{heater_name} is not in the heater dict, cannot read voltage')
        return voltages

    def read_current(self, heater_name):
        """
        read a single current
        heater_name : string which labels the channel
        returns a float of the current
        """
        channel = self.heater_dict.get(heater_name)
        if channel is not None:
            return self.q.i[channel]
        else:
            print(f'{heater_name} is not in the heater dict, cannot read current')

    def read_many_currents(self, heater_names):
        """
        read multiple currents
        heater_names : iterable of heaters to be read
        returns a dict of heater_name : current pairs
        """
        currents = dict()
        for heater_name in heater_names:
            channel = self.heater_dict.get(heater_name)
            if channel is not None:
                currents[heater_name] = self.q.i[channel]
            else:
                print(f'{heater_name} is not in the heater dict, cannot read current')
        return currents

    def read_everything(self, special_timeout=1, temp_t1=0.25, temp_t2=0.25, printing=False):
        t1 = self.q.response_timeout                
        t2 = self.q.inter_response_timeout
        self.q.response_timeout = temp_t1
        self.q.inter_response_timeout = temp_t2 
        readings = self.q.issue_command(command_id='vipall', operator='?', special_timeout=special_timeout)
        self.q.response_timeout = t1 
        self.q.inter_response_timeout = t2 
        if printing:
            print(readings)
        else:
            return readings