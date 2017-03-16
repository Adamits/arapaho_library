# -*- coding: utf-8 -*-

from lexicon import *
from text import *

text = Text()
lexicon = Lexicon()

text.parse("./data/master_text.txt")
lexicon.parse("./data/arapaho_lexicon.json")

print "%d entries in lexicon" % len(lexicon.lexical_entries)
print "%d examples in lexicon" % sum([len(entry.examples) for entry in lexical_parser.lexical_entries])
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
  match_tuples = entry.get_matching_lexeme_pos_tuples_from(mb_ps_tuples)
  # List comprehension to get all text_examples of any lex OR allolexeme in the entry that match its pos
  match_examples = [text_example for match_tuple in match_tuples for text_example in mb_ps_tuples_and_examples[match_tuple]]
  # Increment total examples for logging
  total_examples_count += len(match_examples)
  # Loop over the examples that have this morpheme
  for match_example in match_examples:
    # Generate an Example Object that goes into the lexicon (probably need to namespace this)
    lex_example = Example(match_example.list())
    # Check if that example is in the lexical entry object already
    if not entry.contains_example(lex_example):
      # Add example to the lexical entry object, this will also increment examplefrequency
      entry.add_example(lex_example)
      # Add example frequency based on frequency of entry lex and allolexes in
      # the morpheme breakdown of the example
      #TODO probably need to make this happen in the add_example() method
      entry.examplefrequency += entry.frequency_in_example_morphemes(match_example.get_mb_list())
      # For logging
      examples_to_add_count += 1

print "\n\n============AFTER UPDATES============\n\n"
print "%s total potential examples in text" % total_examples_count
print "%s examples added" % examples_to_add_count
print "%d examples in lexicon after additions" % sum([len(entry.examples) for entry in lexical_parser.lexical_entries])
print "%d frequencies of examples in lexicon after additions" % sum([entry.examplefrequency for entry in lexical_parser.lexical_entries])
print "%d # of entries" % len(lexical_parser.lexical_entries)

with open("./data/new_arapaho_lexicon.json", 'w') as outfile:
  json.dump(lexical_parser.json_format(), outfile)