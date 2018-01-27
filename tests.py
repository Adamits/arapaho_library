# -*- coding: utf-8 -*-

from arapaho_library import corpus

arapaho_corpus = corpus.Corpus()


def get_texts(names=[]):
  """
  Given a list of text names, return a list of Text objects
  """
  return arapaho_corpus.get_texts({"name": {"$in": names}})


t = get_texts(["1"])
print(t)