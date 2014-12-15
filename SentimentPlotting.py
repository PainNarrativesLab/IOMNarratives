"""
This contains classes which are inherited by things that need to plot sentiment data
"""
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import random
#This is my plot tools class
from PlottingTools import JitterPlot as jp

#data = [{'avgPos': 0.25, 'avgNeg': 1.0833333333333333, 'quoteID': 268L}, {'avgPos': 0.3333333333333333, 'avgNeg': 0.20833333333333334, 'quoteID': 303L}, {'avgPos': 0.08333333333333333, 'avgNeg': 0.3958333333333333, 'quoteID': 304L}, {'avgPos': 0.4166666666666667, 'avgNeg': 0.5416666666666666, 'quoteID': 331L}, {'avgPos': 0.397625, 'avgNeg': 0.359375, 'quoteID': 426L}, {'avgPos': 0.4375, 'avgNeg': 0.125, 'quoteID': 448L}, {'avgPos': 0.4375, 'avgNeg': 0.14583333333333334, 'quoteID': 449L}, {'avgPos': 1.0625, 'avgNeg': 0.1875, 'quoteID': 464L}, {'avgPos': 0.3888888888888889, 'avgNeg': 0.75, 'quoteID': 773L}, {'avgPos': 0.140625, 'avgNeg': 0.140625, 'quoteID': 807L}, {'avgPos': 0.25, 'avgNeg': 1.0, 'quoteID': 815L}, {'avgPos': 0.375, 'avgNeg': 0.5625, 'quoteID': 841L}]


class SentimentPlot():
	def __init__(self):
		self.data = data
		self.np = np
		self.plt = plt
				
	def plotLine(self, data):
		"""
		This plots a line chart with lines for avgPos, avgNeg, and netSent
		"""
		self.data = data

		plt.plot(self.avgPos, marker='o', label='Average positive score for vignette sentences')
		plt.plot(self.avgNeg, marker='^', label='Average positive score for vignette sentences')
		plt.plot(self.netSent, marker='p', color='r', label='Average sentiment score (positive - negative) for vignette sentences')
		plt.ylabel('Average sentiment polarities for vignettes')
		plt.title('Sentiment polarities for vignettes')
		plt.legend()
		plt.show()
	
	def scatterPlot(self, xdata, ydata):
		self.data = data

		j = jp(emotot, negSent, .01)
		j.setLabels('emotion tot', 'sum of absolute sentiment values')
		j.plot()
	
	
	def plotBar(self, names, posSent, negSent, netSent):
		"""
		Each parameter is a list
		"""
		##xlocations = np.array(range(len(keys)))+0.5
		labels = names
		width = 0.2
		plt.bar(0, posSent[0], label='TN positive', width=width, color='r')
		plt.bar(0.2, posSent[1], label='CRPS positive', width=width, color='b')
		plt.bar(1, negSent[0], label='TN negative', width=width, color='r')
		plt.bar(1.2, negSent[1], label='TN negative', width=width, color='b')
		plt.bar(2, netSent[0], label='TN net sentiment', width=width, color='r')
		plt.bar(2.2, negSent[1], label='CRPS net sentiment', width=width, color='b')
		##plt.bar(xlocations, netSent, label=labels, width=width)
		##plt.bar(1, posSent)
		plt.legend()
		plt.show()
		#labels = ["Baseline", "System"]
		#data =   [3.75               , 4.75]
		#error =  [0.3497             , 0.3108]
		#xlocations = na.array(range(len(data)))+0.5
		#width = 0.5
		#bar(xlocations, data, yerr=error, width=width)
		#yticks(range(0, 8))
		#xticks(xlocations+ width/2, labels)
		#xlim(0, xlocations[-1]+width*2)
		#title("Average Ratings on the Training Set")
		#gca().get_xaxis().tick_bottom()
		#gca().get_yaxis().tick_left()
		#
		#




		##plt.plot([1,2,3,4])
##plt.ylabel('some numbers')
##plt.show()
##plt.close()
#quoteIDs = []
#avgPos = []
#avgNeg = []
#netSent = []
#for d in data:
#        quoteIDs.append(d['quoteID'])
#        avgPos.append(d['avgPos'])
#        avgNeg.append(d['avgNeg'] * -1)
#        ns = d['avgPos'] + (d['avgNeg'] * -1)
#        print ns
#        netSent.append(ns)
#
#overallpos = np.average(avgPos)
#overallneg = np.average(avgNeg)
#overallsent = np.average(netSent)
#
#print 'average positive sentiment for all vignettes: ' , overallpos
#print overallneg
#print 'overall net ', overallsent
#
###        for ap in d['avgPos']:
###                ap)
###print avgPos
###p = np.arange(avgPos)
###n = np.arange(avgNeg)
#plt.plot(avgPos, marker='o')
#plt.plot(avgNeg, marker='^')
#plt.plot(netSent, marker='p', color='r')
###plt.plot(quoteIDs, avgPos, marker='o')
###plt.plot(quoteIDs, avgNeg, marker='^')
#plt.ylabel('average sentiment polarities by vignette score')
#plt.show()
###plt.close()
