from gensim.models.word2vec import Word2Vec
from sklearn.cluster import KMeans
from corpus import *
import numpy as np
import re
from scipy import spatial

"""
Experimenting with clustering morpheme tags by running kmeans over embeddings
"""

ps_model = Word2Vec.load('../models/ps_embeddings')

corpus = Corpus()

verb_tag_vectors = []
verb_regexes = [r"\b(vai).*", r"\b(vti).*", r"\b(vta).*", r"\b(vii).*"]

for regex in verb_regexes:
  verb_examples = corpus.get_text_examples({'segments.pos': {"$regex": regex}})
  matching_segs = [segment for example in verb_examples for segment in example.get_segments() if
                   re.findall(regex, segment.pos)]
  verb_tag_vectors.append(list(set([t.pos for t in matching_segs])))

embedding_vectors = []
for verb_tag_vector in verb_tag_vectors:
  embedding_vectors.append([ps_model.wv[v] for v in verb_tag_vector])

# Flatten into vector of size tags
data = np.array([e for verbs in embedding_vectors for e in verbs])
kmeans = KMeans(n_clusters=20, random_state=0).fit(data)

print(kmeans.predict(ps_model.wv["vii"].reshape(1, -1)))
print(kmeans.predict(ps_model.wv["vai"].reshape(1, -1)))
print(kmeans.predict(ps_model.wv["vai.o"].reshape(1, -1)))
print(kmeans.predict(ps_model.wv["vai.t"].reshape(1, -1)))
print(kmeans.predict(ps_model.wv["vai.IMPERF"].reshape(1, -1)))
print(kmeans.predict(ps_model.wv["vti"].reshape(1, -1)))
print(kmeans.predict(ps_model.wv["vta"].reshape(1, -1)))
