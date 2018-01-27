from gensim.models.word2vec import Word2Vec
from corpus import *
import numpy as np
from scipy import spatial

"""
Experimenting with finding morpheme class membership by averaging embeddings of morphemes with the same tag.
"""

def get_cosine_similarity(vec_1, vec_2):
  return 1 - spatial.distance.cosine(ps_model.wv["vai.o.incorp"], vai_exemplar)


ps_model = Word2Vec.load('../models/ps_embeddings')

corpus = Corpus()

segment_cursor = corpus.collection.find({}, {"segments.pos": 1, "_id": 0})
all_tags = list(set([segment["pos"] for dict in segment_cursor for segment in dict["segments"]]))

regex_via = re.compile(r"\bvia.*")
verb_examples_via = corpus.get_text_examples({'segments.pos': {"$regex": regex_via}})
matching_segs_via = [segment for example in verb_examples_via for segment in example.get_segments() if
                regex_via.findall(segment.pos)]
via_tags = list(set([t.pos for t in matching_segs_via]))

# Sanity check, lots of tags, smaller # of tags in the regex
print(len(all_tags))
print(len(via_tags))

# Split into train/test data
split = round(len(via_tags) * .8)
train_data = via_tags[:split]
test_data = via_tags[split:]


# Average Vector
vai_train_embeddings = [ps_model.wv[tag] for tag in train_data]
vai_exemplar = np.average(np.array(vai_train_embeddings), axis=0)

# Get most similar to average of embeddings for tags that match the regex
print(ps_model.similar_by_vector(vai_exemplar, 1000))

# part seems super frequent, check against it to see effectiveness
print(get_cosine_similarity(vai_exemplar, "part"))