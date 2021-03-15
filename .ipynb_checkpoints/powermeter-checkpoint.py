
import pyvisa, math, sys
import numpy as np
import time
import matplotlib.pyplot as plt
plt.style.use('ggplot')

class Powermeter(object):

	read_timeout = 0.
	unit = 'mW'			# {'W', 'mW', 'dBm'}
	model = None		# This is populated with the powermeter model, for handling different interfaces. Case sensitive
						# Supported models: N7747A; PM100D; PM100USB

	def __init__(self, model, serial=None, unit=None, wavelength=None, averages=None):

		# Find instrument corresponding to model and serial numbers

		rm = pyvisa.ResourceManager()
		serial_names=rm.list_resources()
		# print(serial_names)

		pm_serial = None
		instrs = []
		for serial_name in serial_names:
			instr = rm.open_resource(serial_name)
			instr.timeout=2

			# if 'model_name' not in dir(instr) or 'serial_number' not in dir(instr):
				# print ('not our instrument')
				# instrs.append({'port':serial_name, 'model':None, 'num':None})
				# continue

			mn = instr.model_name
			sn = instr.serial_number	
			
			instrs.append({'port':serial_name, 'model':mn, 'num':sn})
			instr.close()
			
			if mn == model and (sn == serial or serial is None):
				pm_serial = serial_name
				break

		# If we didn't find any matchin instrument, raise an error
		if pm_serial is None:
			raise StandardError('Unable to find device {0} {1}. Found devices {2}'.format(model, serial, instrs))

		self.instr = rm.open_resource(pm_serial)
		self.model = self.instr.model_name

		# Set up default and initialisation values
		if wavelength is not None:
			self.set_wavelength(wavelength)
		if averages is not None:
			self.set_averages(averages)
		if unit is not None:
			self.unit = unit

			
	def close(self):
		self.instr.close()

	def __del__(self):
		self.close()

	def measure(self, channel = 1):

		if (self.model == 'PM100D' or 'PM100USB'):
			
			result_W = -float('inf')
			n_tries = 5
			for iter in range(n_tries):
				try:
					result_W = float(self.instr.query('read?', delay=self.read_timeout))
				except pyvisa.errors.VisaIOError:
					print ("Caught error during powermeter read '{:}'. Tries remaining: {:}.".format(sys.exc_info()[0], n_tries-iter+1))
					continue
				break
			if iter == n_tries-1:
				try:
					print ('Trying to reinitialise powermeter.')
					self.close()
					self.__init__(self.model)
					result_W = float(self.instr.query('read?', delay=self.read_timeout))
				except:
					raise RuntimeError('Error:Powermeter:measure: Tried {:} times to read powermeter, failed. Tried to reinitialise powermeter, failed.'.format(n_tries))
				
				
		elif (self.model == 'N7747A'):
			if (channel not in [1,2]):
				raise AttributeError ('Channel number for model {0} must be in [1,2]. Specified channel {1} is invalid.'.format(self.model, channel))
			result_W = float(self.instr.query('read{ch}:pow?'.format(ch = channel), delay=self.read_timeout))
		else:
			raise AttributeError('Unknown model "{0}".'.format(self.model))


		if self.unit == 'W':
			return result_W
		elif self.unit == 'mW':
			return result_W * 1000
		elif self.unit == 'dBm':
			return 10 * math.log(result_W * 1000, 10 ) if (result_W > 0) else (-float('Inf'))
		else:
			raise AttributeError('Measurement unit, {0}, unrecognised.'.format(self.unit))


	def query(self,command):
		return float(self.instr.query(command))
	
	def set_wavelength(self, wl_nm):
		self.instr.write('CORR:WAV {0}\n'.format(wl_nm))

	def set_averages(self, n_averages):
		self.instr.write('sens:aver {0}\n'.format(n_averages))

	def measure_average(self,n_averages):
		memo = np.zeros(n_averages)
		for j in range(n_averages):
			memo[j] = self.measure()
		return np.mean(memo)

	def power_live(self,dt=0.1,averages=1,save=False,array_Live=100):
		try:
			get_ipython().magic('matplotlib notebook')
			counter=0
			n_sample=[]
			power=[]
			fig,ax=plt.subplots(figsize=(9,6))
			plt.ylabel('Power (dBm)')
			plt.xlabel('Time flies')
			ax.plot([],[])
			
			while True:
				power.append(self.measure_average(n_averages=averages))
				n_sample.append(counter)
				self.PlotWindowed(ax,n_sample,power,array_Live)
				plt.tight_layout()
				fig.canvas.draw()
				counter+=1
				
				time.sleep(dt)
				
		except KeyboardInterrupt:
			if save is True:
				return power,n_sample
			else:
				None

	def PlotWindowed(self,axes,x,y,array_Live):
		
		axes.lines[0].set_data(x[-min(array_Live,len(x)):],y[-min(array_Live,len(x)):])
		axes.relim()
		axes.autoscale_view()
		return None

def power_live_multiple(*detectors,dt=0.001,array_Live=200):

	n=len(detectors)
	get_ipython().magic('matplotlib notebook')
	fig=plt.figure(figsize=(9,6))
	pwr=([],)
	
	for i in range(n):
		fig.add_subplot(n,1,i+1)
		fig.axes[i].plot([],[])
		pwr=pwr+([],)
			
	fig.subplots_adjust(hspace=0.3)
	while True:
		for i,detector in enumerate(detectors):
			(pwr[i]).append(detector.measure())
			axTemp=fig.axes[i]
			pwrTemp=pwr[i]
			Plot(axTemp,pwrTemp,array_Live)
			axTemp.set_title("{}: {:>4} dBm".format(detector.instr.serial_number,round(pwrTemp[-1],2)))
			time.sleep(dt)
		fig.canvas.draw()
	return Plot(axTemp,pwrTemp,array_Live)

def Plot(ax,y,array_Live):

	ax.lines[0].set_data(np.arange(1,len(y[-min(array_Live,len(y)):])+1),y[-min(array_Live,len(y)):])
	ax.relim()
	ax.autoscale_view()

# def power_live_multiple(*detectors,dt=0.1,averages=1,array_Live):
	
	# get_ipython().magic('matplotlib notebook')
	# fig = plt.figure()
	# n=len(detectors)
	# fig=plt.figure()
	# fig.add_subplot(111)
	# plt.plot([],[])
	# pwr=([],)
	
	# if n>1:
		# for i in range(n):
			# fig.axes[i].change_geometry(n, 1, i+1)
			# fig.add_subplot(n,1,i+1)
			# plt.plot([],[])
			# pwr+([],)
	# while True:
		# for detector in detectors:
			
			# Plot(detector.measure(),array_Live)
			

# def Plot(y,array_Live):
		
	# # axes.lines[0].set_data(x[-min(array_Live,len(x)):],y[-min(array_Live,len(x)):])
	# axes.lines[0].set_ydata(y[-min(array_Live,len(y)):])
	# axes.relim()
	# axes.autoscale_view()
	# return None
		
def list_visa_instruments():
	rm = pyvisa.ResourceManager()
	serial_names=rm.list_resources()

	pm_serial = None
	instrs = []
	for serial_name in serial_names:
		instr = rm.open_resource(serial_name)
		instr.timeout=2

		if 'model_name' not in dir(instr) or 'serial_number' not in dir(instr):
			instrs.append({'port':serial_name, 'model':None, 'num':None})
			continue

		mn = instr.model_name
		sn = instr.serial_number

		instrs.append({'port':serial_name, 'model':mn, 'num':sn})
		instr.close()

	return instrs

#print(list_visa_instruments())
