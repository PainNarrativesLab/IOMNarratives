from ConditionsServiceClasses import ConditionsService

class ConditionDetector(ConditionsService):
	"""
	This finds instances of condition terms in text	
	"""
	
	def __init__(self):
		ConditionsService.__init__(self)
		self.load_conditions()
		self.load_aliases()
		
#	Loop through the condition aliases

# Make a list of unigram aliases

# Make a list of bigram aliases etc

# Starting with the largest unit (e.g., trigrams or maybe specific long phrases?)

# tokenize appropriately after checking how many words in the alias to decide whether to do unigrams, bigrams, etcetera tokens

# Loop through the tokenized text checking against the 
