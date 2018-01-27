from arapaho_library.text import *
import pymongo

conn=pymongo.MongoClient()
db = conn['arapaho_texts']

"""
{ID:, name: TextName, lines: {ref: ref, free_translation: ft, words: {word: word, morphemes: {morpheme: morpheme, pos: pos, gloss: gloss}}}}
"""

class Corpus(object):

  def __init__(self, corpus_name='text_corpus'):
    self.db = db
    self.collections = db.showCollections
    self.collection = db[corpus_name]

  def add_entries(self, text_dicts=[]):
    self.collection.insert_many(text_dicts)

  def get_texts(self, args={}):
    """
    More intuitive method wrapped over get_cursor
    Returns a list of Text objects, implemented in this library
    """
    results = self.get_cursor(args)
    texts = []

    for text_dict in results:
      texts.append(Text(options=text_dict))

    return texts

  # cursor is mongos record set, which is an iterable object of
  # multiple documents. Kind of like SQL records
  def get_cursor(self, args={}):
    return self.collection.find(args)

def run_test():
  arapaho_corpus = Corpus()
  examples = arapaho_corpus.get_text_examples({'mb':{'$regex':'hii3'}})
  refs = set([x.ref for x in examples])
  print(len(refs))

#run_test()