import itertools
from arapaholexicalparser import *
from arapahotextparser import ArapahoTextParser

text_parser = ArapahoTextParser()
lexical_parser = ArapahoLexicalParser()

text_parser.parse()
lexical_parser.parse()

print "%d examples in lexicon" % sum([len(entry.examples) for entry in lexical_parser.where("examplefrequency > 0")])

mbs_and_examples = text_parser.mbs_and_examples()
mbs = mbs_and_examples.keys()

print "%d unique mbs in the text" % len(mbs)
total_examples_count = 0
examples_to_add_count = 0

for entry in lexical_parser.lexical_entries:
  # If this entry appears in the example morphemes
  match = entry.appears_in(mbs)
  if match:
    # get the examples that have a morpheme (mb) of this entry
    match_examples = mbs_and_examples[match]
    # Increment total examples for logging
    total_examples_count += len(match_examples)
    # Loop over the examples that have this morpheme
    for match_example in match_examples:
      # Generate an Example Object that goes into th elexicon (probably need to namespace this)
      lex_example = Example(match_example.list())
      # Check if that example is in the lexical entry object already
      if not entry.contains_example(lex_example):
        # Add example to the liexical entry object
        entry.examples.append(lex_example)
        # Increment examplefrequency
        entry.examplefrequency += 1
        # For logging
        examples_to_add_count += 1

print "%s total examples" % total_examples_count
print "%s examples added" % examples_to_add_count
with open("/Users/ajwieme/Desktop/test_arapaho_lexicon", 'w') as outfile:
  json.dump(lexical_parser.as_json_dict(), outfile)