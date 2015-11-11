#!/usr/bin/env python
"""
Interface to SentiWordNet using the NLTK WordNet classes.

---Chris Potts
"""

import re
import os
import sys
import codecs

try:
    from nltk.corpus import wordnet as wn
except ImportError:
    sys.stderr.write("Couldn't find an NLTK installation. To get it: http://www.nltk.org/.\n")
    sys.exit(2)

######################################################################


class SentiWordNetCorpusReader(object):
    """
    Reads senti word net file
    """
    def __init__(self, filename):
        """
        Args:
            filename: The name of the text file containing the SentiWordNet database
        """
        self.filename = filename
        self.db = {}
        self.parse_src_file()

    def parse_src_file(self):
        lines = codecs.open(self.filename, "r", "utf8").read().splitlines()
        lines = list(filter((lambda x: not re.search(r"^\s*#", x)), lines))
        for i, line in enumerate(lines):
            fields = re.split(r"\t+", line)
            fields = list(map(str.strip, fields))
            try:
                pos, offset, pos_score, neg_score, synset_terms, gloss = fields
            except:
                sys.stderr.write("Line %s formatted incorrectly: %s\n" % (i, line))
            if pos and offset:
                offset = int(offset)
                self.db[(pos, offset)] = (float(pos_score), float(neg_score))

    def senti_synset(self, *vals):
        if tuple(vals) in self.db:
            pos_score, neg_score = self.db[tuple(vals)]
            pos, offset = vals
            synset = wn._synset_from_pos_and_offset(pos, offset)
            return SentiSynset(pos_score, neg_score, synset)
        else:
            synset = wn.synset(vals[0])
            pos = synset.pos
            offset = synset.offset
            if (pos, offset) in self.db:
                pos_score, neg_score = self.db[(pos, offset)]
                return SentiSynset(pos_score, neg_score, synset)
            else:
                return None

    def senti_synsets(self, string, pos=None):
        sentis = []
        synset_list = wn.synsets(string, pos)
        for synset in synset_list:
            sentis.append(self.senti_synset(synset.name))
        sentis = [x for x in sentis if x]
        return sentis

    def all_senti_synsets(self):
        for key, fields in self.db.items():
            pos, offset = key
            pos_score, neg_score = fields
            synset = wn._synset_from_pos_and_offset(pos, offset)
            yield SentiSynset(pos_score, neg_score, synset)


######################################################################


class SentiSynset:
    def __init__(self, pos_score, neg_score, synset):
        self.pos_score = pos_score
        self.neg_score = neg_score
        self.obj_score = 1.0 - (self.pos_score + self.neg_score)
        self.synset = synset

    def __str__(self):
        """Prints just the Pos/Neg scores for now."""
        s = ""
        s += self.synset.name + "\t"
        s += "PosScore: %s\t" % self.pos_score
        s += "NegScore: %s" % self.neg_score
        return s

    def __repr__(self):
        return "Senti" + repr(self.synset)


######################################################################        


if __name__ == "__main__":
    pass

    # """
    # If run as
    #
    # python sentiwordnet.py
    #
    # and the file is in this directory, send all of the SentiSynSet
    # name, pos_score, neg_score trios to standard output.
    # """
    # SWN_FILENAME = "SentiWordNet_3.0.0_20100705.txt"
    # if os.path.exists(SWN_FILENAME):
    #     swn = SentiWordNet(SWN_FILENAME)
    #     for senti_synset in swn.all_senti_synsets():
    #         print(senti_synset.synset.name, senti_synset.pos_score, senti_synset.neg_score)
