import serial 
import  re, time
from collections import deque as fifo
from random import shuffle
from serial import *
# from serial.tools import list_ports
import numpy as np
import matplotlib.pyplot as plt
import time
import re
from scipy.optimize import minimize


class tunics(object):
	"""
	Super class which handles serial communication, device identification, and logging.
	
	serial_port = None                  Serial port object
		serial_port_name = None             Name of serial port, eg 'COM1' or '/dev/tty1'
		response_timeout = 0.050            Timeout for response or error to commands
	"""

	# serial_port = None                      # Serial port object
	# serial_port_name = None                 # Name of serial port, eg 'COM1' or '/dev/tty1'
	baudrate = 9600                         # Serial port baud rate (signalling frequency, Hz)
	response_timeout = 0.200                # Timeout for RESPONSE_OK or error to set commands
	# channel = 'CH6'

	def __init__(self, serial_port_name,channel=None,lambda_range=[1500.,1580.]):
		# constructor
		self.serial_port_name=serial_port_name
		if channel is not None:
			self.channel=channel+':'
		else:
			self.channel=''
		try:
			self.serial_port = serial.Serial(self.serial_port_name, self.baudrate, timeout=self.response_timeout)
		except:
			raise AttributeError("No device found on port {}".format(self.serial_port_name))
		
        # Set a time benchmark
		self.init_time = time.time()
		print ('\nConnected to Tunics laser on serial port {0}\n'.format(self.serial_port_name))
		# self.get_lambda_range()
		self.LAM_min=lambda_range[0]
		self.LAM_max=lambda_range[1]
		print("LAM min:",self.LAM_min,end=' ')
		print("LAM max:",self.LAM_max)
	
	
	def close(self):
		"""
		Destructor.
		"""
		# Close serial port
		if self.serial_port is not None and self.serial_port.is_open:
			self.serial_port.close()
	
	def transmit(self, command_string):
		"""
		Low-level transmit data method.
		"""
		# Ensure serial port is open
		if not self.serial_port.is_open:
			self.serial_port.open()
		
		# Write to port
		self.serial_port.write(command_string.encode('utf-8'))
        
	def receive(self):
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

	def set_echo(self,echo=1):
		echo_dict=['OFF','ON']
		self.transmit(self.channel+'ECHO'+echo_dict[echo]+'\r')

	def get_lambda_range(self):
		self.transmit(self.channel+'L? MIN\r')
		time.sleep(.1)
		LAM_min_response=(self.serial_port.readline()).decode('utf-8')
		print(LAM_min_response)
		self.LAM_min = [float(lam) for lam in re.findall('\d+\.\d+',LAM_min_response)][0]
		self.transmit(self.channel+'L? MAX\r')
		time.sleep(.1)
		LAM_max_response=(self.serial_port.readline()).decode('utf-8')
		self.LAM_max = [float(lam) for lam in re.findall('\d+\.\d+',LAM_max_response)][0]
		return self.LAM_min,self.LAM_max

	def mw_or_dbm(self,val='MW'):
		self.transmit(self.channel+val+'\r')

	def get_laser_wavelength(self):
		self.transmit(self.channel+'L?\r') 
		response=[]
		while 'L=' not in response:
			response = str(self.serial_port.readline().decode())
		return [float(lam) for lam in re.findall('\d+\.\d+',response)][0]

	def get_laser_power(self):
		self.transmit(self.channel+'P?\r') 
		response=[]
		while 'P=' not in response:
			response = str(self.serial_port.readline().decode())			

		return [float(p) for p in re.findall('\d+\.\d+',response)][0]
		
	def laser_wavelength(self,wavelength):
		if self.LAM_min<=wavelength<=self.LAM_max:
			self.transmit(self.channel+'L={0: 4.4f}\r'.format(wavelength))  
		else:
			raise RuntimeError(['Wavelength not in acceptable range ',self.LAM_min,' < lambda < ',self.LAM_max,' nm'])

		# return self.get_laser_wavelength() 
#

	# def laser_wavelength(self,wavelength):
	#     if self.LAM_min<=wavelength<=self.LAM_max:
	#         self.transmit('CH2:L={0: 4.4f}\r'.format(wavelength))  
	#     else:
	#         raise RuntimeError(['Wavelength not in acceptable range ',self.LAM_min,' < lambda < ',self.LAM_max,' nm'])

	#     return None
		
		
	def laser_power(self,power):
		if 0<=power<=25:
			self.transmit(self.channel+'P={0: 4.4f}\r'.format(power))   
		else:
			raise RuntimeError('Power not in acceptable range 0 < P < 25 mW')
		return None
	
		
	# def laser_switch(self,switch):
	#     if switch==1:
	#         cmd='CH2:ENABLE\r'
	#         self.transmit(cmd)
	#     else:
	#         cmd='CH2:DISABLE\r'
	#         self.transmit(cmd)  
	#     return None

	def laser_switch(self,switch):
		if switch==1:
			cmd=self.channel+'ENABLE\r'
			self.transmit(cmd)
		else:
			cmd=self.channel+'DISABLE\r'
			self.transmit(cmd)  
		return None
	



	def make_spectra(self,lam_min,lam_max,npts,timelag,ave_meas,detectors):
		# check that the detectors are a particular model
		try:
			if str(detectors[0].model) == 'PM100USB':
				pass
			else:
				raise RuntimeError('The detector is not a PM100USB')
		except Exception as ex:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			message = template.format(type(ex).__name__, ex.args)
			print (message)

		# check that wavelength limits fall within the range of the laser
		if lam_min<self.LAM_min:
			raise RuntimeError('Inserted lower wavelength bound is too short. Should be in the interval {0}-{1}'.format(OsicsMainframe.LAM_min,OsicsMainframe.LAM_max))
		elif lam_max>self.LAM_max:
			raise RuntimeError('Inserted upper wavelength bound is too high. Should be in the interval {0}-{1}'.format(OsicsMainframe.LAM_min,OsicsMainframe.LAM_max))
		else:
			# generate a numpy array of wavelength values between lam_min and lam_max
			wavelengths = np.linspace(lam_min,lam_max,npts)
			# count number of detectors objects
			nd = len(detectors)
			# create figure for data, size depends on number of detectors
			fig = plt.figure(figsize=(9, 4*nd))
			# generate a tuple of lists to store detector measurements
			power_readings = ([],)

			# generate subplots and add a list to tuple for each detector
			for i in range(nd):
				fig.add_subplot(nd, 1, i + 1)
				fig.axes[i].plot([], [])
				if i != 0:
					power_readings = power_readings + ([],)

			# set spacing between subplots
			fig.subplots_adjust(hspace=0.3)

			# set intial wavelength and allow time for laser to stablise
			self.laser_wavelength(wavelengths[0])
			time.sleep(15)

			# cycle through wavelength values
			for j, wavelength in enumerate(wavelengths):
				# set wavelength of laser
				self.laser_wavelength(wavelengths[j])
				# time delay required to allow for wavelength adjustment
				time.sleep(timelag)

				# cycle through detectors and record the measured powers
				for i, det in enumerate(detectors):
					#print("detector: " + str(i))
					# set detection wavelength of detector
					det.set_wavelength(wavelengths[j])
					# append an averaged detector power reading to list within tupl
					(power_readings[i]).append(det.measure_average(ave_meas))
				
				# plots the data for each detector
				for i,ax in enumerate(fig.axes): 
					ax.clear()
					ax.grid()
					ax.minorticks_on()
					ax.grid(which='major', linestyle='-', linewidth='0.5', color='black')
					ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
					ax.set_xlim([lam_min, lam_max])
					ax.set(xlabel='Wavelength', ylabel='Power (dBm)')
					ax.plot(wavelengths[0:j + 1], power_readings[i])

				# enables a live plotting of the data
				fig.canvas.draw()
		# return a tuple: array of wavelength values and array of array of power readings 
		return np.round(wavelengths,3),np.round(power_readings,3)



	# def get_coincidences(self,SNSPD,integration_time):
	#     packet=SNSPD.integrate(integration_time)
	#     coincidences=packet['coincidences']
 
	def active_wavelength_tuning(self,detector,lam0,range_lam,threshold,resolution=0.001,):
		# def cost_function(lam):
		#     self.laser_wavelength(lam)
		#     return detector.measure_average(4)
		# minimize(cost_function,lam0,method='COBYLA',rhobeg=0.001,catol=0.001)

		lam=lam0
		self.laser_wavelength(lam)
		detector.set_wavelength(lam)
		power1 = detector.measure_average(4)
		lam+=resolution
		self.laser_wavelength(lam)

		lam_array=[]
		power_array=[]
		index_array=[]
		index=1
		slide=200

		fig,ax1=plt.subplots(2)
		ax1[0].plot([],[])
		ax1[1].plot([],[])
		# ax2=ax1.twinx()

		def tune_lambda(lam,power1):

			detector.set_wavelength(lam)
			power = detector.measure_average(4)
			if power>power1:
				lam-=resolution
			else:
				lam+=resolution
			new_lam=self.laser_wavelength(lam)
			detector.set_wavelength(new_lam)
			power1 = detector.measure_average(4)
			index_array=range(1,index+1)
			# print(new_lam,"  ",np.round(power1,2))
			# lam_array.append(new_lam)
			power_array.append(power1)
			ax1.cla()
			# ax.cla()
			# ax2.cla()
			# ax1.set_xlim(range_lam[0],range_lam[1])
			# ax1.vlines(new_lam,0,1)
			# # ax1.plot(new_lam)
			ax1.plot(power1)
			fig.canvas.draw()
			index+=1

		try:
			while 1:
				# tune_lambda(lam,power1)
				detector.set_wavelength(lam)
				power = detector.measure_average(4)
				if power1>threshold:
					if power>power1:
						lam-=resolution
					else:
						lam+=resolution
				new_lam=self.laser_wavelength(lam)
				power1 = power#detector.measure_average(10)
				index_array=range(1,index+1)
				# print(new_lam,"  ",np.round(power1,2))
				# lam_array.append(new_lam)
				power_array.append(power1)
				lam_array.append(new_lam)
				ax1[0].cla()
				ax1[1].cla()
				# ax1.set_xlim(range_lam[0],range_lam[1])
				# ax1.vlines(new_lam,0,1)
				# # ax1.plot(new_lam)
				ax1[0].plot(index_array[-min(len(index_array),slide):-1],power_array[-min(len(index_array),slide):-1])
				ax1[1].plot(index_array[-min(len(index_array),slide):-1],lam_array[-min(len(index_array),slide):-1])
				ax1[0].set_title(str(new_lam))
				# ax1[1].set_ylim(range_lam[0],range_lam[1])
				fig.canvas.draw()
				index+=1
		except (KeyboardInterrupt, SystemExit):
			print("Interrupted by user.")


	def active_wavelength_tuning_Ste(self,detector,lam0,range_lam,threshold,resolution=0.001,):
		# def cost_function(lam):
		#     self.laser_wavelength(lam)
		#     return detector.measure_average(4)
		# minimize(cost_function,lam0,method='COBYLA',rhobeg=0.001,catol=0.001)

		lam=lam0
		self.laser_wavelength(lam)
		# power1 = detector.measure_average(4)
		# lam+=resolution
		# self.laser_wavelength(lam)

		lam_array=[]
		power_array=[]
		index_array=[]
		index=1
		slide=200

		fig,ax1=plt.subplots(2)
		ax1[0].plot([],[])
		ax1[1].plot([],[])
		# ax2=ax1.twinx()

		power = detector.measure_average(4)

		mysign=+1

		try:
			while 1:
				# tune_lambda(lam,power1)
				if power>threshold:

					templam=lam + mysign*resolution
					self.laser_wavelength(templam)
					power_temp = detector.measure_average(4)

					if power_temp<power:
						power=power_temp
						lam=templam
					else:
						self.laser_wavelength(lam)
						mysign=-1*mysign
						
				power = detector.measure_average(4)
				index_array=range(1,index+1)
				# print(new_lam,"  ",np.round(power1,2))
				# lam_array.append(new_lam)
				power_array.append(power)
				lam_array.append(lam)
				ax1[0].cla()
				ax1[1].cla()
				# ax1.set_xlim(range_lam[0],range_lam[1])
				# ax1.vlines(new_lam,0,1)
				# # ax1.plot(new_lam)
				ax1[0].plot(index_array[-min(len(index_array),slide):-1],power_array[-min(len(index_array),slide):-1])
				ax1[1].plot(index_array[-min(len(index_array),slide):-1],lam_array[-min(len(index_array),slide):-1])
				ax1[0].set_title(str(lam))
				# ax1[1].set_ylim(range_lam[0],range_lam[1])
				fig.canvas.draw()
				index+=1
		except (KeyboardInterrupt, SystemExit):
			print("Interrupted by user.")

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