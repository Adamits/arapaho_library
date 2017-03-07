from arapahotextparser import TextExample
import pymongo

conn=pymongo.MongoClient()
db = conn['arapaho_texts']
corpus = db['text_corpus']

class CorpusText(object):

  def add_entries(self, text_example_jsons=[]):
    db.corpus.insert_many(text_example_jsons)

  def get_text_examples(self, args={}):
    results = self.get_cursor(args)
    examples_array = []

    for result in results:
      examples_array.append(TextExample(result))

    return examples_array

  def get_cursor(self, args={}):
    return corpus.find(args)