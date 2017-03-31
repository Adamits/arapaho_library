# -*- coding: utf-8 -*-

from lexicon import *
from text import *

text = Text()
lexicon = Lexicon()

text.parse("../data/77b.txt")
lexicon.parse("../data/arapaho_lexicon.json")

print "%d entries in lexicon" % len(lexicon.lexical_entries)
print "%d examples in lexicon" % sum([len(entry.examples) for entry in lexicon.lexical_entries])
print "%d examples in lexicon according to examplefrequencies" % sum([entry.examplefrequency for entry in lexicon.lexical_entries])

mb_ps_tuples_and_examples = text.mb_ps_tuples_and_examples()
mb_ps_tuples = mb_ps_tuples_and_examples.keys()

print "%d unique mbs in the text" % len(set(mb_ps_tuples))
total_examples_count = 0
examples_to_add_count = 0

# Clear all of the examples to start for consistancy
lexicon.remove_all_entry_examples()

#TODO OPTIMIZE THIS BAD BOY
for entry in lexicon.lexical_entries:
  # Get the examples that have a morpheme (mb) and the pos (ps) of this entry
  match_tuples = entry.get_match_from(mb_ps_tuples)
  # Get all text_examples of any lex OR allolexeme in the entry that match its pos
  # Look for a matching ge in the example to confirm
  match_examples = []
  for match_tuple in match_tuples:
    for text_example in mb_ps_tuples_and_examples[match_tuple]:
      # TODO change to reflect that we only care about instances where get_ge_list() is not the
      # TODO same length as mb_list, and look for isntances where a gloss is multiple words/symbols seperated by whitespace.
      if entry.gloss in ' '.join(text_example.get_ge_list()):
        match_examples.append(text_example)
  # Increment total examples for logging
  total_examples_count += len(match_examples)
  # Loop over the examples that have this morpheme
  for match_example in match_examples:
    # Generate an Example Object that goes into the lexicon (probably need to namespace this)
    print entry.lex_and_allolex_list()
    print entry.pos
    print entry.gloss
    print match_example.get_mb_list()
    print match_example.get_ps_list()
    print match_example.get_ge_list()

#with open("../data/new_arapaho_lexicon.json", 'w') as outfile:
#  json.dump(lexicon.json_format(), outfile)