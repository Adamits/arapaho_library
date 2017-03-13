import itertools
from arapaholexicalparser import *
from arapahotextparser import ArapahoTextParser

text_parser = ArapahoTextParser()
lexical_parser = ArapahoLexicalParser()

#text_parser.parse()
lexical_parser.parse("./data/test_arapaho_lexicon.json")

print "%d entries in lexicon" % len(lexical_parser.lexical_entries)
print "%d examples in lexicon" % sum([len(entry.examples) for entry in lexical_parser.where("examplefrequency > 0")])

#print "%d unique lexemes in text" % len(set(list(itertools.chain.from_iterable(mb_lists))))

#print "%d examples in text" %  len(text_parser.examples)

def find_duplicates():
  return True

def json_format_test():
  entry = lexical_parser.lexical_entries[0]
  print entry.examples[0].ft
  return entry.json_format()

def is_adding_duplicates():
  mbs_and_examples = text_parser.mbs_and_examples()
  mbs = mbs_and_examples.keys()
  for entry in lexical_parser.lexical_entries:
    # If this entry appears in the example morphemes
    match = entry.appears_in(mbs)
    if match:
      # get the examples that have a morpheme (mb) of this entry
      match_examples = mbs_and_examples[match]
      # Loop over the examples that have this morpheme
      for match_example in match_examples:
        # Generate an Example Object that goes into th elexicon (probably need to namespace this)
        lex_example = Example(match_example.list())
        # Check if that example is in the lexical entry object already
        if not entry.contains_example(lex_example):
          # Add example to the liexical entry object
          entry.add_example(lex_example)
          # Increment examplefrequency
          entry.examplefrequency += 1

#is_adding_duplicates()
# print len(lexical_parser.where("examplefrequency > 100"))