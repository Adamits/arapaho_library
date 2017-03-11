import itertools
from arapaholexicalparser import *
from arapahotextparser import ArapahoTextParser

text_parser = ArapahoTextParser()
lexical_parser = ArapahoLexicalParser()

#text_parser.parse()
lexical_parser.parse()

print "%d examples in lexicon" % sum([len(entry.examples) for entry in lexical_parser.where("examplefrequency > 0")])

#print "%d unique lexemes in text" % len(set(list(itertools.chain.from_iterable(mb_lists))))

#print "%d examples in text" %  len(text_parser.examples)

def as_json_dict_test():
  entry = lexical_parser.lexical_entries[0]
  print entry.examples[0].ft
  return entry.as_json_dict()

print len(lexical_parser.where("examplefrequency > 100"))