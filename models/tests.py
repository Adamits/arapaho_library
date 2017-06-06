# Ideas w/ word embeddings:
## In the db, sometimes a single lexeme stores many content morphemes combined (often w/ phonotactic changes)
## Can we find these, and see how closely embeddings know that they are related, vis a vis some examples that might appear
## appear to be similar, but actually are not?
## How do these relate to the mb_embeddings?
"""
import logging
from gensim.models.word2vec import Word2Vec

word_model = Word2Vec.load('./word_embeddings')

#print word_model.wv.vocab
print word_model.wv.similarity("nonoohobei'ee", "nonoo'oenoo'oo'")
print word_model.wv.similarity("Niineyeihei'towuuno'", "niineyei3itooP")
print word_model.wv.similarity("Heetneeciini", "heetneenin")
print word_model.wv.similarity("neesootox", "neesootoxu3i'")

mb_model = Word2Vec.load('./ps_embeddings')
print "============="

#print mb_model.wv.vocab
print mb_model.wv.similarity("vti", "vai")
print mb_model.wv.similarity("vti", "via")
print mb_model.wv.similarity("vta", "vti")
print mb_model.wv.similarity("vta", "via")
print mb_model.wv.similarity("vai.incorp", "vai.incorp+pl")
"""

import spacy
nlp = spacy.load('en')
print nlp

test = nlp(u"Hey I am Adam")
for token in test:
  print (token.text, token.pos_, token.pos)