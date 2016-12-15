# -*- coding: utf-8 -*-

import sys
import json

import nltk


class cosine_simiarlity_analyzer():
    def __init__(self, list_of_texts, data):
        """
        @param list_of_texts List of dictionaries containing tokenized word bags each with a 'quote_id' and 'quote_text' or 'tokens' attributes
        """
        self.similar_quotes = []
        # Will hold list of dictionaries with rootID, friendID, tfidf_score
        self.most_similar = []
        #Will hold list of dictionaries with rootID, friendID, tfidf_score
        self.similarities = []

        self.data = data
        #Create a list with all bag contents
        self.texts = []
        for bag in list_of_texts:
            try:
                self.texts.extend(bag['quote_text'])
            except:
                self.texts.extend(bag['tokens'])


        # Provides tf/idf/tf_idf abstractions for scoring
        self.tc = nltk.TextCollection(self.texts)
        # Compute a term-document matrix such that td_matrix[doc_title][term]
        # returns a tf-idf score for the term in the document
        self.td_matrix = {}
        for idx in range(len(self.data)):
            post = self.data[idx]['quote_text']
            fdist = nltk.FreqDist(post)
            doc_title = self.data[idx]['quote_id']
            try:
                link = self.data[idx]['quote_text']
            except:
                link = self.data[idx]['tokens']

            self.td_matrix[(doc_title, link)] = {}

            for term in fdist.keys():
                self.td_matrix[(doc_title, link)][term] = self.tc.tf_idf(term, post)

        # Build vectors such that term scores are in the same positions...
        self.distances = {}
        for (title1, link1) in list(self.td_matrix.keys()):
            self.distances[(title1, link1)] = {}
            (max_score, most_similar) = (0.0, (None, None))
            for (title2, link2) in list(self.td_matrix.keys()):
                # Take care not to mutate the original data structures
                # since we're in a loop and need the originals multiple times
                terms1 = self.td_matrix[(title1, link1)].copy()
                terms2 = self.td_matrix[(title2, link2)].copy()
                # Fill in "gaps" in each map so vectors of the same length can be computed
                for term1 in terms1:
                    if term1 not in terms2:
                        terms2[term1] = 0
                for term2 in terms2:
                    if term2 not in terms1:
                        terms1[term2] = 0
                # Create vectors from term maps
                v1 = [score for (term, score) in sorted(terms1.items())]
                v2 = [score for (term, score) in sorted(terms2.items())]
                # Compute similarity amongst documents
                self.distances[(title1, link1)][(title2, link2)] = \
                    nltk.cluster.util.cosine_distance(v1, v2)
                self.similarities.append(
                    dict(rootID=title1, friendID=title2, tfidf_score=nltk.cluster.util.cosine_distance(v1, v2)))
                if link1 == link2:
                    continue

                if self.distances[(title1, link1)][(title2, link2)] > max_score:
                    (max_score, most_similar) = (self.distances[(title1, link1)][(title2, link2)], (title2, link2))
                    self.similar_quotes.append((title1, link1, most_similar[0], most_similar[1], max_score))
                    self.most_similar.append(dict(rootID=title1, friendID=most_similar[0], tfidf_score=max_score))
                #print '''Most similar to %s (%s) \t%s (%s)\tscore %s''' % (title1, link1, most_similar[0], most_similar[1], max_score)

    def provis_output(self):
        # Compute the standard deviation for the distances as a basis of automated thresholding
        std = numpy.std([self.distances[k1][k2] for k1 in self.distances for k2 in self.distances[k1]])
        self.similar = []
        keys = list(self.td_matrix.keys())
        for k1 in keys:
            for k2 in keys:
                if k1 == k2:
                    continue
                d = self.distances[k1][k2]
                if d < std / 2 and d > 0.000001:  # call them similar
                    (title1, link1) = k1
                    (title2, link2) = k2
                    self.similar.append((k1, k2, distances[k1][k2]))

        # Emit output expected by Protovis.
        nodes = {}
        node_idx = 0
        edges = []
        for s in self.similar:
            if s[0] not in nodes:
                nodes[s[0]] = node_idx
                node_idx += 1

            node0 = nodes[s[0]]

            if s[1] not in nodes:
                nodes[s[1]] = node_idx
                node_idx += 1

            node1 = nodes[s[1]]
            edges.append({'source': node0, 'target': node1, 'value': s[2] * 1000})

        nodes = [{'nodeName': title, 'nodeUrl': url} for ((title, url), idx) in
                 sorted(list(nodes.items()), key=itemgetter(1))]
        json_data = {'nodes': nodes, 'links': edges}
        # This json_data is consumed by matrix_diagram.html
        if not os.path.isdir('out'):
            os.mkdir('out')
        # HTML_TEMPLATE references some Protovis scripts, which we can
        # simply copy into out/
        shutil.rmtree('out/protovis-3.2', ignore_errors=True)
        shutil.copytree('../web_code/protovis/protovis-3.2',
                        'out/protovis-3.2')
        for template in HTML_TEMPLATES:
            html = open(template).read() % (json.dumps(json_data),)
            f = open(os.path.join(os.getcwd(), 'out', os.path.basename(template)), 'w')
            f.write(html)
            f.close()
            print('Data file written to: %s' % f.name, file=sys.stderr)
            webbrowser.open('file://' + f.name)