import numpy as np
import ZeroLevel_Qontrol as q0
import FirstLevel_Qontrol as q1


class heater_class:

	def __init__(self,COM_PORTS,heater_dict):

		self.COM1 = COM_PORTS[0]
		self.COM2 = COM_PORTS[1]
		self.COM3 = COM_PORTS[2]

		self.heater_dict = heater_dict

		self.heater_dict1 = {name: heater_dict.get(name)[1] for name in heater_dict.keys() if heater_dict.get(name)[0] == 0}
		self.heater_dict2 = {name: heater_dict.get(name)[1] for name in heater_dict.keys() if heater_dict.get(name)[0] == 1}
		self.heater_dict3 = {name: heater_dict.get(name)[1] for name in heater_dict.keys() if heater_dict.get(name)[0] == 2}

		self.max_voltage1 = {name: heater_dict.get(name)[2] for name in heater_dict.keys() if heater_dict.get(name)[0] == 0}
		self.max_voltage2 = {name: heater_dict.get(name)[2] for name in heater_dict.keys() if heater_dict.get(name)[0] == 1}
		self.max_voltage3 = {name: heater_dict.get(name)[2] for name in heater_dict.keys() if heater_dict.get(name)[0] == 2} 





		b1 = q0.QXOutput(serial_port_name=self.COM1, response_timeout=0.1)
		heaters1 =q1.HeaterQontrol(b1,self.heater_dict1,self.max_voltage1)


		b2 = q0.QXOutput(serial_port_name=self.COM2, response_timeout=0.1)
		heaters2 =q1.HeaterQontrol(b2, self.heater_dict2, self.max_voltage2)

		b3 = q0.QXOutput(serial_port_name=self.COM3, response_timeout=0.1)
		heaters3 =q1.HeaterQontrol(b3, self.heater_dict3, self.max_voltage3)


		self.heaters_array = [heaters1,heaters2,heaters3]
	def set_voltage(self,heater_name,voltage):

		which_board = self.heater_dict[heater_name][0]
		heater =self.heaters_array[which_board].set_voltage(heater_name,voltage)

            
	def read_current(self, heater_name):
		which_board=self.heater_dict[heater_name][0]
		heater = self.heaters_array[which_board].read_current(heater_name)
		return heater

        
	def set_all_zeros_bad(self):
		board1_zero = {name: self.heaters_array[0].set_voltage(name,0) for name in self.heater_dict.keys() if self.heater_dict.get(name)[0] == 0}
		board2_zero = {name: self.heaters_array[1].set_voltage(name,0) for name in self.heater_dict.keys() if self.heater_dict.get(name)[0] == 1}
		board3_zero = {name: self.heaters_array[2].set_voltage(name,0) for name in self.heater_dict.keys() if self.heater_dict.get(name)[0] == 2}

	def set_many_phases(self, names_phases_dict, chunk_size=4, sleep_time=0.02):
		for name in names_phases_dict.keys():
			which_board = self.heater_dict[name][0]
			phase = names_phases_dict[name]
			heater = self.heaters_array[which_board].set_phase(name, phase)
			#v = self.heaters_array[which_board].phase_to_voltage(name, phase)
			#self.heaters_array[which_board].set_voltage(name, v)

	def set_phase(self, heater_name, phase):
		which_board = self.heater_dict[heater_name][0]
		heater = self.heaters_array[which_board].set_phase(heater_name, phase)
        


	def set_all_zeros(self):
		self.b1.set_all_zeros()
		def close_all(self):#in progress
			closing1=self.b1.close()
			#self.serial_port.close()"""
	def close_all(self):
		b1.close()
		b2.close()
		b3.close()
        
		"""def set_all_zeros(self,me):
			f=3*me
			self.b1.issue_command(command_id='vall', operator='=', value=0)  
			self.b2.issue_command(command_id='vall', operator='=', value=0)  
			self.b3.issue_command(command_id='vall', operator='=', value=0)  
		"""