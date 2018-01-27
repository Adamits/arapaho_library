# Ideas w/ word embeddings:
## In the db, sometimes a single lexeme stores many content morphemes combined (often w/ phonotactic changes)
## Can we find these, and see how closely embeddings know that they are related, vis a vis some examples that might appear
## appear to be similar, but actually are not?
## How do these relate to the mb_embeddings?

import logging
import numpy as np
from gensim.models.word2vec import Word2Vec

'''
word_model = Word2Vec.load('./word_embeddings')

#print word_model.wv.vocab
print word_model.wv.similarity("nonoohobei'ee", "nonoo'oenoo'oo'")
print word_model.wv.similarity("Niineyeihei'towuuno'", "niineyei3itooP")
print word_model.wv.similarity("Heetneeciini", "heetneenin")
print word_model.wv.similarity("neesootox", "neesootoxu3i'")

print "============="
'''
#print mb_model.wv.vocab
mb_model = Word2Vec.load('./ps_embeddings')
print mb_model
print mb_model.wv["vai"]
print mb_model.wv["vai.t"]
print np.average(zip(mb_model.wv["vai"], mb_model.wv["vai.t"]), axis=1)
#print mb_model.wv["vai"]#index2word[1700]
#mb_model.wv["test_average"] = [sum(x) / 2.0 for x in zip(mb_model.wv["vai.o"], mb_model.wv["vai"])]
