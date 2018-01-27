# -*- coding: utf-8 -*-
from corpus import *
import re
import logging
from gensim.models.word2vec import Word2Vec

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

corpus = Corpus()

examples = corpus.get_all_text_examples()

#print len(examples)
sentences = [re.split(r'\s+', example.tx) for example in examples]
# train word2vec on the two sentences
model = Word2Vec(sentences, min_count=1)

model.save('../models/word_embeddings')