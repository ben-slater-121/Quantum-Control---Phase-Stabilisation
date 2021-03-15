import serial 
import  re, time
from collections import deque as fifo
from random import shuffle
from serial import *
# from serial.tools import list_ports
import numpy as np
import matplotlib.pyplot as plt
import time


class tunics(object):
	"""
	Super class which handles serial communication, device identification, and logging.
	
	serial_port = None					Serial port object
		serial_port_name = None				Name of serial port, eg 'COM1' or '/dev/tty1'
		response_timeout = 0.050			Timeout for response or error to commands
	"""

	serial_port = None						# Serial port object
	serial_port_name = None					# Name of serial port, eg 'COM1' or '/dev/tty1'
	baudrate = 9600							# Serial port baud rate (signalling frequency, Hz)
	response_timeout = 0.200				# Timeout for RESPONSE_OK or error to set commands
	LAM_max =1610
	LAM_min =1490
	channel = 'CH2'
	

	def __init__(self, *args, **kwargs):
		#Initialiser.
		# Get arguments from init
		# Populate parameters, if provided
		# LAM_max = self.LAM_max
		# LAM_min = self.LAM_min
		
		for para in ['serial_port_name', 'response_timeout', 'baudrate']:
			try:
				self.__setattr__(para, kwargs[para])
			except KeyError:
				continue

			
		if 'serial_port_name' in kwargs:

			self.serial_port = serial.Serial(self.serial_port_name, self.baudrate, timeout=self.response_timeout)
			# self.serial_port = Serial(self.serial_port_name, self.baudrate, timeout=self.response_timeout)
		else:
			raise AttributeError('At least serial_port_name must be specified on Qontroller initialisation.')
		
		# Set a time benchmark
		self.init_time = time.time()
		print ('\nConnected to Tunics laser on serial port {0}\n'.format(self.serial_port_name))
	
	
	def __del__(self):
		"""
		Destructor.
		"""
		# Close serial port
		#if self.serial_port is not None and self.serial_port.is_open:
		self.serial_port.close()
	
	def close(self):
		self.serial_port.close()

	def transmit (self, command_string):
		"""
		Low-level transmit data method.
		"""
		# Ensure serial port is open
		if not self.serial_port.is_open:
			self.serial_port.open()
		
		# Write to port
		self.serial_port.write(command_string.encode('utf-8'))

	
	
	def receive (self):
		"""
		Low-level receive data method which also checks for errors.
		"""
		# Ensure serial port is open
		if not self.serial_port.is_open:
			self.serial_port.open()
		
		# Read from port
		lines = []
		errs = []
		
		# Check if there's anything in the input buffer
		while self.serial_port.in_waiting > 0:
			# Get a line from the receive buffer
			line = self.serial_port.readline().decode('utf-8')
			
			# Check if it's an error by parsing it
			err = self.parse_error(line)
			if err is None:
				# No error, keep the line
				lines.append(line)
			else:
				# Line represents an error, add to list
				errs.append(err)
		
		# Add any errors we found to our log
		for err in errs:
			self.log_append(type='err', id=err['id'], ch=err['ch'], desc=err['desc'])
		
		return (lines, errs)

	
	def wait (self, seconds=0.0):
		"""
		Do nothing while watching for errors on the serial bus.
		"""
		start_time = time.time()
		while time.time() < start_time + seconds:
			self.receive()
	
	def switch_channel(self,channel):
		if channel is 1 or channel is 2 or channel is 3 or channel is 4:
			self.transmit('CH4:CH={0: 4.4f}\r'.format(channel))	
		else:
			raise RuntimeError(['Wrong channel selection, must be 1, 2, 3 or 4 '])

		return None

	def laser_wavelength(self,wavelength):
		if self.LAM_min<=wavelength<=self.LAM_max:
			self.transmit('L={0: 4.4f}\r'.format(wavelength))	
		else:
			raise RuntimeError(['Wavelength not in acceptable range ',self.LAM_min,' < lambda < ',self.LAM_max,' nm'])

		return None
		
		
	def laser_power_watts(self,power):
		if 0<=power<=25:
			self.transmit('P={0: 4.4f}\r'.format(power))
		else:
			raise RuntimeError('Power not in acceptable range 0 < P < 25 mW')
		return None
    
	def laser_power(self,power):
		if -3<=power<=14:
			self.transmit('P={0: 4.4f}\r'.format(power))
		else:
			raise RuntimeError('Power not in acceptable range -3 < P < 14 mW')
		return None
		
		
	def laser_switch(self,switch):
		if switch==1 or switch=='on':
			self.transmit('ENABLE\r')
		else:
			self.transmit('DISABLE\r')	
		return None
	
			
	def make_spectra(self,lam_min,lam_max,npts,detector1,detector2,detector3,timelag,averages,shift):		
		try:
			if str(detector1.model) == 'PM100USB':
				pass
			else:
				raise RuntimeError('The detector is not a PM100USB')
		except Exception as ex:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			message = template.format(type(ex).__name__, ex.args)
			print (message)
				
		if lam_min<=tunics.LAM_min:
			raise RuntimeError('Inserted lower wavelength bound is too short. Should be in the interval {0}-{1}'.format(OsicsMainframe.LAM_min,OsicsMainframe.LAM_max))
		elif lam_max>=tunics.LAM_max:
			raise RuntimeError('Inserted upper wavelength bound is too high. Should be in the interval {0}-{1}'.format(OsicsMainframe.LAM_min,OsicsMainframe.LAM_max))
		else:
			self.laser_switch(1)
			wav = np.linspace(lam_min,lam_max,npts)
			pwr = []
			pwr2 = []
			pwr3 = []		
			
			for counter,w in enumerate(wav):
				# print(counter)
				if counter == 0:
					self.laser_wavelength(wav[counter])
					print('Going to initial wavelength')
					time.sleep(5+timelag)
					if detector2 is not None:
						fig1, ax = plt.subplots(2,figsize=(8, 6))
					else:
						fig1, ax = plt.subplots(1,figsize=(8, 6))
					# ax1 = fig1.add_subplot(211)
					# ax2 = fig1.add_subplot(212)
					fig1.show()
					# fig2, ax2 = plt.subplots(212)
					# fig2.show()
				# else:
					# self.laser_wavelength(wav[counter])
					# time.sleep(timelag)
					# pwr[counter]=detector1.measure_average(averages)
					# if detector2 is not None:
						# pwr2[counter] = detector2.measure_average(averages)	
						# if detector3 is not None:
							# pwr3[counter] = detector3.measure_average(averages)						
							# print('Wavelength: {0} -- Power detector 1: {1} {2} -- Power detector 2: {3} {4} -- Power detector 3: {5} {6}'.format(wav[counter],pwr[counter],detector1.unit,pwr2[counter],detector2.unit,pwr3[counter],detector3.unit))
					# elif detector3 is not None:
						# pwr3[counter] = detector3.measure_average(averages)
						# print('Wavelength: {0} -- Power detector 1: {1} {2} -- -- Power detector 3: {3} {4}'.format(wav[counter],pwr[counter],detector1.unit,pwr3[counter],detector3.unit))
			# #self.laser_switch(0)
				self.laser_wavelength(wav[counter])
				detector1.set_wavelength(wav[counter])
				time.sleep(timelag)
				pwr.append(detector1.measure_average(averages))
				if detector2 is not None:
					ax0=ax[0]
					ax1=ax[1]
				else:
					ax0=ax
				ax0.clear()# plt.cla()
				ax0.grid()
				ax0.minorticks_on()
				ax0.grid(which='major', linestyle='-', linewidth='0.5', color='black')
				ax0.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
				# plt.gca().set_ylim([min(0,min(pwr))-0.1,max(0,max(pwr))+0.1])
				# pos=-min(len(pwr2),200)
				# print(pos)
				# if counter is not 0:
				ax0.set_xlim([lam_min-shift,lam_max-shift])
				ax0.set(xlabel='Wavelength', ylabel='Power (dBm)')
				# ax[0].set_ylim([min(pwr),max(0,pwr)])
				# comp=[np.nan]*(npts-counter-1)
				# pwr1Plot=pwr
				# pwr1Plot.append(comp)
				# print str('wav : ')+str(len(wav[0:counter]))
				# print str('pwr')+str(len(pwr))
				# print pwr
				ax0.plot(wav[0:counter+1]-shift,pwr)
				
				# print [wav[counter],' : 'pwr[counter]]
				if detector2 is not None:
					detector2.set_wavelength(wav[counter])
					pwr2.append(detector2.measure_average(averages))
					# print [pwr[-1],pwr2[-1]]
					# ax2.cla()
					ax1.clear()# plt.cla()
					ax1.grid()
					ax1.minorticks_on()
					ax1.grid(which='major', linestyle='-', linewidth='0.5', color='black')
					ax1.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
					# plt.gca().set_ylim([min(0,min(pwr))-0.1,max(0,max(pwr))+0.1])
					# ax[1].set_ylim([min(pwr2),max(pwr2,0)])
					# if counter is not 0:
					ax1.set_xlim([lam_min-shift,lam_max-shift])
					ax1.plot(wav[0:counter+1]-shift,pwr2)
					ax1.set(xlabel='Wavelength', ylabel='Power (dBm)')
					if detector3 is not None:
						# detector3.set_wavelength(wav[counter])
						pwr3.append(detector3.measure_average(averages))					
						# print('Wavelength: {0} -- Power detector 1: {1} {2} -- Power detector 2: {3} {4} -- Power detector 3: {5} {6}'.format(wav[counter],pwr[counter],detector1.unit,pwr2[counter],detector2.unit,pwr3[counter],detector3.unit))
					else:
						pwr3=None
				else:
					pwr2=None
					# print('Wavelength: {0} -- Power detector 1: {1} {2} -- -- Power detector 3: {3} {4}'.format(wav[counter],pwr[counter],detector1.unit,pwr3[counter],detector3.unit))
				
				fig1.suptitle('Transmission spectrum')
				
				
				# ax[0].xlabel('Wavelength', fontsize=5)
				# ax[0].ylabel('Transmission (dBm)', fontsize=5)
				# ax[1].xlabel('Wavelength', fontsize=5)
				# ax[1].ylabel('Transmission (dBm)', fontsize=5)
				plt.show()
				fig1.canvas.draw()
		return [wav,pwr,pwr2]	
		
	"""
	from powermeter import * #this is also importing pyvisa
	from tunicsqontrol import tunics
	import matplotlib.pyplot as plt
	
	mypow1 = Powermeter('PM100USB', serial='P2010190', unit='dBm', wavelength=1550)
	mypow2 = Powermeter('PM100USB', serial='P2010191', unit='dBm', wavelength=1550)
	
	mytunics = tunics(serial_port_name = 'COM39')
	wav,pwr1,pwr2,pwr3 = mytunics.make_spectra(1540,1560,100,mypow1,mypow2,None)	
	plt.plot(wav,pwr1)
	"""