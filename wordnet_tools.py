from nltk.corpus import wordnet as wn
from collections import defaultdict

"""
These are methods and funtions for working with wordNet style synsets
"""


def synset_method_values(synset):
    """
    For a given synset, get all the (method_name, value) pairs
    for that synset. Returns the list of such pairs.
    """
    name_value_pairs = []
    # All the available synset methods:
    method_names = ['hypernyms', 'instance_hypernyms', 'hyponyms', 'instance_hyponyms', 'member_holonyms',
                    'substance_holonyms', 'part_holonyms', 'member_meronyms', 'substance_meronyms', 'part_meronyms',
                    'attributes', 'entailments', 'causes', 'also_sees', 'verb_groups', 'similar_tos']
    for method_name in method_names:
        # Get the method's value for this synset based on its string name.
        method = getattr(synset, method_name)
        vals = method()
        name_value_pairs.append((method_name, vals))
    return name_value_pairs
