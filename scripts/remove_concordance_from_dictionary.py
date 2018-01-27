# -*- coding: utf-8 -*-

from lexicon import *

lexicon = Lexicon()

lexicon.parse("../data/arapaho_lexicon.json")

print("%d entries in lexicon" % len(lexicon.lexical_entries))
print("%d examples in lexicon" % sum([len(entry.examples) for entry in lexicon.lexical_entries]))
print("%d examples in lexicon according to examplefrequencies" % sum([entry.examplefrequency for entry in lexicon.lexical_entries]))

# Clear all of the examples to start for consistancy
lexicon.remove_all_entry_examples()

with open("../data/new_arapaho_lexicon.json", 'w') as outfile:
  json.dump(lexicon.json_format(), outfile)