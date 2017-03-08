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

print len(mbs)
total_examples_count = 0
examples_to_add_count = 0

for entry in lexical_parser.lexical_entries:
  # If this entry appears in the example
  match = entry.appears_in(mbs)
  if match:
    match_examples = mbs_and_examples[match]
    entry.examplefrequency += len(match_examples)
    total_examples_count += len(match_examples)
    for match_example in match_examples:
      lex_example = Example(match_example.list())
      if not entry.contains_example(lex_example):
        entry.examples.append(lex_example)
        examples_to_add_count += 1

print "%s total examples" % total_examples_count
print "%s total examples" % examples_to_add_count
with open("/Users/ajwieme/Desktop/test_arapaho_lexicon", 'w') as outfile:
  json.dump(lexical_parser.as_json_dict(), outfile)