from text import *
import pymongo

conn=pymongo.MongoClient()
db = conn['arapaho_texts']

class Corpus(object):

  def __init__(self, corpus_name='text_corpus'):
    self.db = db
    self.collections = db.showCollections
    self.collection = db[corpus_name]

  def add_entries(self, text_example_dicts=[]):
    self.collection.insert_many(text_example_dicts)

  # More intuitive method wrapped over get_cursor
  # Returns a list of TextExamples, implemented in this library
  def get_text_examples(self, args={}):
    results = self.get_cursor(args)
    text_examples = []

    for example_dict in results:
      text_examples.append(TextExample(example_dict))

    return text_examples

  # cursor is mongos record set, which is an iterable object of
  # multiple documents. Kind of like SSQL records
  def get_cursor(self, args={}):
    return self.collection.find(args)

def run_test():
  arapaho_corpus = Corpus()
  examples = arapaho_corpus.get_text_examples({'mb':{'$regex':'hii3'}})
  refs = set([x.ref for x in examples])
  print len(refs)

#run_test()