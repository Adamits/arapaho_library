"""
INPUT: Text object, which contains many TextExamples
of IGT. Add these to the corpus of examples, which is
implemented as a mongodb.
"""

from corpus import *
from text import *

def add_text_to_corpus(text=Text()):
  corpus = Corpus()
  corpus.add_entries([example.__dict__ for example in text.examples])

  return corpus