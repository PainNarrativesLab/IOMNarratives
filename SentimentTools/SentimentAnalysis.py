"""
This contains classes used for analyzing the sentiments of input texts
"""

import re
import pprint
import shelve

# import IOMDataService as DS

# from TextFiltration import Sentences, Words, Lemmatized, Bigrams, Trigrams
import numpy as np

from senti_classifier import senti_classifier

import nltk
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize


class SentiSynsetTools(object):
    """
    Tools for loading and working with SentiWordNet stuff
    """

    def load_senti_synsets_for_word(self, word):
        """
        Get a list of senti_synsets for the word

        Args:
            word: String to lookup

        Returns:
            List of senti_synsets

        Example:
            input: slow
            result:
                SentiSynset('decelerate.v.01'),
                SentiSynset('slow.v.02'),
                SentiSynset('slow.v.03'),
                SentiSynset('slow.a.01'),
                SentiSynset('slow.a.02'),
                SentiSynset('slow.a.04'),
                SentiSynset('slowly.r.01'),
                SentiSynset('behind.r.03')]
        """
        return list(swn.senti_synsets('slow'))

    def get_scores_from_senti_synset(self, string_name_of_synset, return_format=tuple):
        """
        Args:
            string_name_of_synset: The string name of the synset that want scores for
            return_format: What kind of object to return. Allowed values are tuple, dict
        Returns:
            On default of tuple returns (positiveScore, negativeScore, objScore)
        """
        breakdown = swn.senti_synset(string_name_of_synset)

        if return_format is tuple:
            return (breakdown.pos_score(), breakdown.neg_score(), breakdown.obj_score())
        elif return_format is dict:
            return {
                'posScore': breakdown.pos_score(),
                'negScore': breakdown.neg_score(),
                'objScore': breakdown.obj_score()
                }


class DisambiguationTools(object):
    """

    """

    def disambiguate_word_senses(self, sentence, word):
        """
        Attempts to determine the proper sense of the target
        word from the sentence in which it appears.

        Args:
            sentence: String representation of the sentence
            word: String represtnation of word

        Returns:
            Returns a synset which is the best guess.

        Example:
            disambiguateWordSenses('A cat is a good pet', 'cat')
            OUT: Synset('cat.v.01')
        """
        wordsynsets = wn.synsets(word)
        bestScore = 0.0
        result = None
        for synset in wordsynsets:
            for w in nltk.word_tokenize(sentence):
                score = 0.0
                for wsynset in wn.synsets(w):
                    sim = wn.path_similarity(wsynset, synset)
                    if(sim == None):
                        continue
                    else:
                        score += sim
                if (score > bestScore):
                    bestScore = score
                    result = synset
        return result


class TextPrepare(object):
    """
    All tools for preparing text for processing
    """

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stop_words.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}']) # remove it if you need punctuation

    def prepare_text(self, tweet_text):
        """
        Returns a bag of words

        Prospective
            Remove emoticons

        :param tweet_text:
        :return: list
        """

        return [i.lower() for i in wordpunct_tokenize(tweet_text) if i.lower() not in self.stop_words]


class ComputeSentiments(object):
    """

    """

    def __init__(self):
        self.text_preparer = TextPrepare()
        self.disambiguator = DisambiguationTools()
        self.sentitools = SentiSynsetTools()


    def compute_sentiments(self, tweet_text):
        """

        :param tweet_text:
        :return:
        """
        tokens = self.text_preparer.prepare_text(tweet_text)

        for word in tokens:
            best_synset = self.disambiguator.disambiguate_word_senses(word, tweet_text)

            # Compute the scores
            scores_tuple = self.sentitools.get_scores_from_senti_synset(best_synset)





class ItemSentimentAnalyzer(object):
    """
    This analyzes and returns the sentiment scores for a particular item
    """

    def __init__(self):
        pass
#        DS.IOMService.__init__(self)

    def computeSentimentScores(self, record, tokenizer):
        """
        record is a dict which must have record['quote_text']. It normally should have record['quote_id'] or record['vin_id']
        tokenizer is a tokenizer with a tokenize method. The unit of analysis (e.g., word, ngram, sentence) is determined by the tokenizer passed in
        """
        self.text = record['quote_text']

        # To allow this to be used with arbitrary inputs
        try:
            self.quoteID = record['quote_id']
        except:
            try:
                self.quoteID = record['vin_id']
            except:
                # Make random ID if none exists
                self.quoteID = 'ID' + str(np.random.rand())

        # Tokenize the text into the appropriate units
        self.tokens = tokenizer.tokenize(self.text)

        # Calc number of tokens in the record
        self.numTokens = len(self.tokens)

        # Calc sentiment scores
        self.pos_score, self.neg_score = senti_classifier.polarity_scores(self.tokens)

        # Averages are needed because otherwise the score will vary with number of sentences
        # Average positive sentiment score of the record
        self.avgPos = self.pos_score / self.numTokens

        # Average negative sentiment of the record
        self.avgNeg = (self.neg_score / self.numTokens) * -1

        # Net average sentiment of the record
        self.netSent = self.avgPos + self.avgNeg

        # Objectivity score (from chris potts )
        self.obj_score = 1.0 - self.netSent

        # Put the results in a dictionary
        self.scores = dict(quoteID=self.quoteID, avgPos=self.avgPos, avgNeg=self.avgNeg, netSent=self.netSent)

        return self.scores

    #def makeDict(self):
    #	"""
    #	Makes a dictionary for the result
    #	Keys: quote_id, avgPos, avgNeg, netSent
    #	"""
    #	self.result_dict = dict(quote_id=self.quote_id, avgPos=self.avgPos, avgNeg=self.avgNeg, netSent=self.netSent)
    #	return self.result_dict

    def saveSentiments(self, filepath):
        """
        Saves the results
        Args:
            filepath: the path to the shelve file where the data is / is to be stored
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
        Args:
            data: a list of dictionaries that have been prepared by ItemSentiments to be saved
            groupname: the name that the result will be stored with/ or the name to retrieve
        """
        self.name = groupname
        #self.datafile = datafile
        self.quoteIDs = []
        self.avgPos = []
        self.avgNeg = []
        self.netSent = []
        for d in data:
            self.quoteIDs.append(d['quote_id'])
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
        self.sentiments = dict(name=self.name, overallpos=self.overallpos, overallneg=self.overallneg,
                               overallsent=self.overallsent)
        db = shelve.open(filepath)
        db[str(self.sentiments['name'])] = self.sentiments
        db.close()
        print(self.sentiments)


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
