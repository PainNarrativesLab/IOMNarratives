"""
This contains classes used for analyzing the sentiments of input texts
"""
from __future__ import division
import IOMDataService as DS
import nltk, re, pprint
#from TextFiltration import Sentences, Words, Lemmatized, Bigrams, Trigrams
import numpy as np
from senti_classifier import senti_classifier


class ItemSentimentAnalyzer(DS.IOMService):
	"""
	This analyzes and returns the sentiment scores for a particular item
	"""
	def __init__(self):
		DS.IOMService.__init__(self)
		
	def computeSentimentScores(self, record, tokenizer):
		"""
		record is a dict which must have record['quoteText']. It normally should have record['quoteID'] or record['vin_id']
		tokenizer is a tokenizer with a tokenize method. The unit of analysis (e.g., word, ngram, sentence) is determined by the tokenizer passed in
		"""
		self.text = record['quoteText']
		#To allow this to be used with aribitrary inputs
		try:
			self.quoteID = record['quoteID']
		except:
			try:
				self.quoteID = record['vin_id']
			except:
				#Make random ID if none exists
				self.quoteID = 'ID' + str(np.random.rand())		
		#Tokenize the text into the appropriate units
		self.tokens = tokenizer.tokenize(self.text)
		#Calc number of tokens in the record
		self.numTokens = len(self.tokens)
		#Calc sentiment scores
		self.pos_score, self.neg_score = senti_classifier.polarity_scores(self.tokens)
		#Averages are needed because otherwise the score will vary with number of sentences
		#Average positive sentiment score of the record
		self.avgPos = self.pos_score/self.numTokens
		#Average negative sentiment of the record
		self.avgNeg = (self.neg_score/self.numTokens) * -1
		#Net average sentiment of the record
		self.netSent = self.avgPos + self.avgNeg
		#Objectivity score (from chris potts )
		self.obj_score = 1.0 - self.netSent
		#Put the results in a dictionary
		self.scores = dict(quoteID=self.quoteID, avgPos=self.avgPos, avgNeg=self.avgNeg, netSent=self.netSent)
		return self.scores

	#def makeDict(self):
	#	"""
	#	Makes a dictionary for the result
	#	Keys: quoteID, avgPos, avgNeg, netSent
	#	"""
	#	self.result_dict = dict(quoteID=self.quoteID, avgPos=self.avgPos, avgNeg=self.avgNeg, netSent=self.netSent)
	#	return self.result_dict
		
	def saveSentiments(self, filepath):
		"""
		Saves the results
		filepath is the path to the shelve file where the data is / is to be stored
		"""
		#self.makeDict()
		self.to_save = self.scores
		self.save_sentiment_data_to_file(filepath)
	

class GroupSentiments:
	"""
	This is used to compute the sentiment scores for a group of items
	"""
	def __init__(self, data, groupname):
		"""
		data is a list of dictionaries that have been prepared by ItemSentiments to be saved
		groupname is the name that the result will be stored with/ or the name to retrieve
		"""
		self.name = groupname
		#self.datafile = datafile
		self.quoteIDs = []
		self.avgPos = []
		self.avgNeg = []
		self.netSent = []
		for d in data:
		    self.quoteIDs.append(d['quoteID'])
		    self.avgPos.append(d['avgPos'])
		    self.avgNeg.append(d['avgNeg'])
		    self.netSent.append(d['netSent'])
		self.overallpos = np.average(self.avgPos)
		self.overallneg = np.average(self.avgNeg)
		self.overallsent = np.average(self.netSent)
	
	def saveSentiments(self, filepath):
		"""
		Saves the results
		
		@param filepath The path to the saved data or to where it should be saved
		@type string
		"""
		self.sentiments = dict(name=self.name, overallpos=self.overallpos, overallneg=self.overallneg, overallsent=self.overallsent)
		db = shelve.open(filepath)
		db[str(self.sentiments['name'])] = self.sentiments
		db.close()
		print self.sentiments

class MultiItemSentimentAnalyzer(ItemSentimentAnalyzer):
	def __init__(self, data_to_analyze, tokenizer, filepath, label):
		"""
		@param data_to_analyze List of dictionaries with items that itemsentimentanalzer can operate on
		@type list
		"""
		ItemSentimentAnalyzer.__init__(self)
		self.to_save = []
		for record in data_to_analyze:
			self.computeSentimentScores(record, tokenizer)
			self.to_save.append(self.scores)
		self.save_sentiment_data_to_file(filepath, label)
