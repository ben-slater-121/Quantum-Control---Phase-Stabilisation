# AM 06/2019

import sys
import numpy as np

try:
	import TimeTagger
except:
	print ("Time Tagger lib is not in the search path.")
	pyversion = sys.version_info
	from winreg import ConnectRegistry, OpenKey, HKEY_LOCAL_MACHINE, QueryValueEx
	registry_path = "SOFTWARE\\Python\\PythonCore\\" + str(pyversion.major) + "." + str(pyversion.minor) + "\\PythonPath\\Time Tagger"
	reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
	key = OpenKey(reg, registry_path) 
	module_path = QueryValueEx(key,'')[0]
	print ("adding " + module_path)
	sys.path.append(module_path)
	
from TimeTagger import createTimeTagger,freeTimeTagger, Coincidences, Counter, Countrate, Correlation,DelayedChannel, CHANNEL_UNUSED, UNKNOWN, LOW, HIGH

from time import sleep
import matplotlib.pyplot as plt
plt.style.use('ggplot')

class TimeTaggerObject:
	"""FUNCTIONS:\n\n
	get_singles(channels=[list],binwidth=[ps],integration_time=[s],delay=[ps],trigger=[V],live=[False],dt=[s],plotTorF=[False])\n
	get_histogram(channels=[list],binwidth=[ps],integration_time=[s],histogram_window=[ns],delay=[ps],trigger=[V],live=[False],dt=[s],plotTorF=[False])\n
	get_coincidences(channels=[list of lists],integration_time=[s],coincidenceWindow=[ns],delay=[ps],trigger=[V],live=[False],dt=[s],binwidth=[ps],plotTorF=[False])\n
	TestSignal(channels=[list],onORoff=[False])\n
	setTrigger(channels=[list],trigger=[V])\n
	setDelay(channels=[list],delay=[ps])\n
	"""
	def __init__(self,channels,delays,triggers,user_name='Alex',array_Live=100,delay_Hardware=1e5,scriptORnotebook = 'notebook'):
		self.tagger = createTimeTagger()
		self.tagger.reset()

		self.user_name = user_name
		self.delay_Hardware = int(delay_Hardware)
		self.array_Live = array_Live
		print('TimeTagger created.\n')
		self.dictOnOff={True:"enabled",False:"disabled"}
		self.scriptORnotebook = scriptORnotebook
		self.channels = channels

		self.setDelay(channels=channels,delay=delays)
		
		self.setTrigger(channels=channels,trigger=triggers)

	def __del__(self):
		self.tagger.reset()
	def close_connection(self):
		return freeTimeTagger(self.tagger)
	def duplicate_channels(self,delayed_channels,delays):
		print(delayed_channels)
		print(delays)
		if isinstance(delays,list):
			print('here1')
			[DelayedChannel(self.tagger,channel,delay) for channel,delay in zip(delayed_channels,delays)]
		else:
			print('here2')
			[DelayedChannel(self.tagger,channel,delays) for channel in delayed_channels]

		return
	def get_channels(self):
		return self.tagger.getChannelList()
	def get_singles(self,
					  channels,
					  binwidth=None,
					  integration_time=None,
					  live=False,
					  dt=None,
					  plotTorF=False,
					  delay_Hardware=1e6):
		
		self.which_method = "singles"
		
		if integration_time is None:
				raise TypeError('"integration_time" value must be provided')
				
		legend=self.create_legend(channels)
		# get_ipython().magic('matplotlib notebook')
		
		
		
		if live is True:
			
			if dt is None:
				raise TypeError('"dt" value must be provided')

			data=[]
			timeArray=[]
			
			count = Counter(tagger=self.tagger, channels=channels, binwidth=int(dt*1e12), n_values=1)
			self.tagger.sync()
			
			
			fig,ax=plt.subplots(figsize=(9,6));
			
			plt.xlabel('Time [seconds]')
			plt.ylabel('Singles count rate [Hz]')
			plt.title('Single Counts after {} seconds'.format(integration_time))
			[ax.plot([],[],label=legend[i]) for i in range(len(channels))]
			plt.legend(loc='upper left',prop={'size': 8})
			plt.tight_layout()
			
			for i in range(int(integration_time/dt)):
				count.startFor(int(dt*1e12+delay_Hardware),clear=True)#+delay_Hardware/dt
				while (count.isRunning()):
					None

				data.append( np.transpose(count.getData())[0] )
				counts=np.transpose(data)/float(dt)
				timeArray.append(dt*(i)+(count.getCaptureDuration())/1e12-delay_Hardware/1e12)
				self.PlotWindowed(ax,timeArray,counts)
				fig.canvas.draw()

			return timeArray,counts
		
		else:
			
			if binwidth is None:
				raise TypeError('"binwdith" value must be provided')
			if integration_time is None:
				raise TypeError('"integration_time" value must be provided')
				
			binwidth=int(binwidth)
			n_values = int((integration_time*1e12)/binwidth)
			
			
			
			count = Counter(tagger=self.tagger, channels=channels, binwidth=binwidth, n_values=n_values)
			sleep(integration_time+delay_Hardware/1e12)
			if plotTorF is True:
				plt.figure();
				[plt.plot(count.getIndex/1e3,count.getData[i]) for i in range(len(channels))];
				plt.legend(np.array(legend),loc='upper left',prop={'size': 8})
				plt.title('Coincidence Counts after {} seconds'.format(integration_time))
				plt.show()
			return count.getIndex(),count.getData()

	def get_histogram(self,
				  channels,
				  binwidth=None,
				  integration_time=None,
				  histogram_window=None,
				  live=False,
				  dt=None,
				  plotTorF=False,
				  delay_Hardware=1e6):
		###
		# binwidth in picoseconds and histogram window in nanoseconds
		###
		self.which_method = "histogram"
		if np.shape(np.array(channels))!=(2,):
			raise TypeError('"channels" must contain a list of 2 channels only')
			
		if integration_time is None:
				raise TypeError('"integration_time" value must be provided')
				
		if binwidth is None:
			raise TypeError('"binwidth" value must be provided')
			
		if histogram_window is None:
			raise TypeError('"histogram_window" value must be provided')
		
		histogram_window = int(histogram_window*1e3)
		binwidth = int(binwidth)
		n_bins = int(histogram_window/binwidth)
		
		
		corr = Correlation(tagger=self.tagger,channel_1=channels[0],channel_2=channels[1],binwidth=binwidth,n_bins=n_bins)
		index = corr.getIndex()/1e3
		self.tagger.sync()
		legend=self.create_legend(channels)
		# get_ipython().magic('matplotlib notebook')
		
		if live is True:
			
			if dt is None:
				raise TypeError('"dt" value must be provided')


			data = np.zeros(n_bins)
			fig,ax = plt.subplots(figsize=(9,6))
			
			plt.xlabel('Time [ns]')
			plt.ylabel('Counts')
			plt.plot([],[],label=legend)
			plt.legend(loc='upper right',prop={'size': 8})
			plt.tight_layout()
			
			for i in range(int(integration_time/dt)):
				corr.startFor(int(dt*1e12+delay_Hardware/dt),clear=False)
				while corr.isRunning():
					None
					
				data = corr.getData()
				self.Plot(ax,index,data)
				
				fig.canvas.draw()

				
			plt.title('Correlation after {} seconds'.format(integration_time))
		
		else:	
			
			sleep(integration_time+0.5)
			index=corr.getIndex()/1e3
			data=corr.getData()
			if plotTorF is True:
				plt.figure()
				plt.plot(index,data,label=legend)
				plt.legend(loc='upper right',prop={'size': 8})
				plt.xlabel('Time [ns]')
				plt.ylabel('Counts')
				plt.xlim(min(index),max(index))
				plt.title('Correlation after {} seconds.'.format(integration_time))
				plt.tight_layout()
				plt.show()
		
		return index,data

	def get_coincidences(self,
					  channels,
					  integration_time=None,
					  coincidenceWindow=None,
					  live=False,
					  dt=None,
					  binwidth=None,
					  plotTorF=False,
					  delay_Hardware=1e6):

		self.which_method = "coincidences"
		try:
			channels[0][0]
		except:
			raise RuntimeError("channels must be of the form [[0,1],[0,2,3]]")
		if integration_time is None:
				raise TypeError('"integration_time" value must be provided')
		# if dt is None:
		# 	raise TypeError('"dt" value must be provided')        

			# extra_channels = [19+i for i in range(len(delayed_channels))]
			# channels += extra_channels
		
		coin = Coincidences(self.tagger,channels,int(1000*coincidenceWindow)) 
		
		legend=self.create_legend(channels)
		# get_ipython().magic('matplotlib notebook')
		
		if live is True:
			
			if dt is None:
				raise TypeError('"dt" value must be provided')
			
			timeArray=[]
			data=[]
			countrate = Counter(self.tagger,channels=coin.getChannels(),binwidth=int(1e12*dt),n_values=1)
			self.tagger.sync()
			fig,ax=plt.subplots(figsize=(9,6));
			
			plt.xlabel('Time [seconds]')
			plt.ylabel('Coincidence count rate [Hz]')
			plt.title('Coincidence Counts after {} seconds'.format(integration_time))
			
			[ax.plot([],[],label=legend[i]) for i in range(len(channels))]
			plt.legend(loc='upper left',prop={'size': 8})
			plt.tight_layout()
			
			for i in range(int(integration_time/dt)):
				countrate.startFor(int(dt*1e12+delay_Hardware/dt),clear=True)
				while countrate.isRunning():
					None
				data.append( np.transpose(countrate.getData())[0] );
				timeArray.append(dt*(i)+(countrate.getCaptureDuration())/1e12-delay_Hardware/1e12);
				counts=np.transpose(data)/float(dt)
				self.PlotWindowed(ax,timeArray,counts)
				
				fig.canvas.draw()

		else:
			if binwidth is None:
				raise TypeError('"binwdith" value must be provided')
			
			binwidth=int(binwidth)
			n_values = int((integration_time*1e12)/binwidth)
			countrate = Counter(self.tagger,channels=coin.getChannels(),binwidth=binwidth,n_values=n_values)
			self.tagger.sync()
			
			sleep(integration_time+0.5)
			timeArray=countrate.getIndex()/1e3
			counts=countrate.getData()
			
			if plotTorF is True:
				plt.figure();
				[plt.plot(counts[i]) for i in range(len(channels))];
				plt.legend(legend,loc='upper left',prop={'size': 8})
				plt.xlabel('Time [seconds]')
				plt.ylabel('Coincidence count rate [Hz]')
				plt.title('Coincidence Counts after {} seconds'.format(integration_time))
				plt.show()
			
		return timeArray,counts

	def TestSignal(self,channels, onORoff=False):
	
		tagger=self.tagger
		tagger.setTestSignal(channels,onORoff)
		for i in range(len(channels)):
			print('CH{} {}\n'.format(channels[i], self.dictOnOff[onORoff])) 

	def setDelay(self,channels,delay):
		assert len(channels)==len(delay)
		[self.tagger.setInputDelay(channels[i], delay[i]) for i in range(len(channels))]
		print("Delays set.")

	def setTrigger(self,channels,trigger):
		assert len(channels)==len(trigger)
		[self.tagger.setTriggerLevel(channels[i], trigger[i]) for i in range(len(channels))]
		print("Triggers set.")


	def getDelay(self,channels=None):
		if channels is None:
			channels=self.channels
		delays = [self.tagger.getInputDelay(channel) for channel in channels]
		return np.array([list(channels),delays])
		

	def getTrigger(self,channels):
		if channels is None:
			channels=self.channels
		triggers = [self.tagger.getTriggerLevel(channel) for channel in channels]
		return np.array([list(channels),triggers])
		

	def PlotWindowed(self,axes,x,y):
		
		for i,line in enumerate(axes.lines):
			line.set_data(x[-min(self.array_Live,len(x)):],y[i,-min(self.array_Live,len(x)):])
		axes.relim()
		axes.autoscale_view()
		return None

	def Plot(self,axes,x,y):
		
		# for i,line in enumerate(ax.lines):
			# if len(ax.lines)==1:
				# line.set_data(x,y)
			# else:
				# line.set_data(x,y[i])
		axes.lines[0].set_data(x,y)
		axes.relim()
		axes.autoscale_view()
		axes.set_xlim(min(x),max(x))
		return None

	def create_legend(self,channels):
		legend=[]
		for i,channel in enumerate(channels):
			legconfig=str(channel)
			legconfig.replace('[','')
			legconfig.replace(']','')
			legend.append(legconfig)
		if self.which_method is not "histogram":
			None
		else:
			legend = '['+', '.join(legend)+']'
			
		return legend
