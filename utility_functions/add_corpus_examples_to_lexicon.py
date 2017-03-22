from corpus import *

def add_corpus_examples_to_lexicon(example_refs=[]):
  corpus = Corpus()

  examples_to_add = corpus.get_text_example({"ref": { "$in": {example_refs}})
