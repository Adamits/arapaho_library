# -*- coding: utf-8 -*-

from lexicon import *
from corpus import *
from analyzer import *
import codecs

text = Text()
lexicon = Lexicon()

#text.parse("./data/master_text.txt")
#lexicon.parse("./data/arapaho_lexicon.json")


# print "%d  of %d examples cannot align gloss, %d percent of examples" % (len(alignment_issues), len(text.examples), float(len(alignment_issues)) / float(len(text.examples)))
# with open("../Desktop/alignment_issues.txt", "w") as out:
# out.write('\n\n'.join(alignment_issues).encode('utf-8').strip())

corpus = Corpus()

#corpus.collection.remove()

#corpus.add_entries(text.examples_as_dicts())

'''
examples = text.examples

tags = []
for example in examples:
  for mb_ps in example.mb_and_ps_tuples():
    tags.append("%s\t%s" % (mb_ps[0], mb_ps[1]))

with codecs.open("./data/pos_tags.txt", 'w', encoding="Latin-1") as outfile:
  outfile.write('\n'.join(tags))


x = corpus.get_text_examples({"ge": {"$regex": "\Wdo s\.t\."}})
print len(x)
for ex in x:
  print ex.get_mb_list()
  print ex.ge

'''

#analyzer = Analyzer(corpus)
#analyzer.all_pos_counts()

#analyzer.write("./data/analysis.txt")

def do_analysis():
  #exact_matches_list = ["na", "ni", "vai", "vai.o", "vai.t", "vii", "vii.impers", "vti", "vta", "PST*", "FUT*",
  #                      "IMPERF*", "PERF*", "IMPER*", "NEG*", "INTERR*", "SUBJ*", "ITER*", "DEP.PART*"]
  searches = [r"\b(vai).*", r"\b(vaa).*", r"\b(vti).*", r"\b(vta).*", r"\b(vii).*"]

  analyzer = Analyzer(corpus)
  analyzer.log_totals()
  for regex in searches:
    analyzer.pos_counts_regex(re.compile(regex))

  analyzer.write("./data/analysis.txt")

do_analysis()

def compare_glosses():
  vtis = lexicon.where("pos is vti")

  for vti in vtis:
    return vti

def validate_matches():
  entries = lexicon.lexical_entries
  for entry in entries:
    # entry.get_matching_lexeme_pos_tuples_from()
    return ""


def write_small_lexicon():
  small_json_dict = {}

  mb_ps_tuples_and_examples = text.mb_ps_tuples_and_examples()
  mb_ps_tuples = mb_ps_tuples_and_examples.keys()

  # TODO OPTIMIZE THIS BAD BOY
  for entry in lexicon.lexical_entries:
    # Get the examples that have a morpheme (mb) and the pos (ps) of this entry
    match_tuples = entry.get_matching_lexeme_pos_tuples_from(mb_ps_tuples)
    # List comprehension to get all text_examples of any lex OR allolexeme in the entry that match its pos
    match_examples = [text_example for match_tuple in match_tuples for text_example in
                      mb_ps_tuples_and_examples[match_tuple]]
    entry.remove_examples()
    # Increment total examples for logging
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
        # TODO probably need to make this happen in the add_example() method
        entry.examplefrequency += entry.frequency_in_example_morphemes(match_example.get_mb_list())
        small_json_dict.update(entry.json_format())

  print "DUMP DAT DATA!"
  with open("./data/small_test_lexicon.json", 'w') as outfile:
    json.dump(small_json_dict, outfile)


KEYNOTFOUND = '<KEYNOTFOUND>'  # KeyNotFound for dictDiff


def dict_diff(first, second):
  """ Return a dict of keys that differ with another config object.  If a value is
      not found in one fo the configs, it will be represented by KEYNOTFOUND.
      @param first:   Fist dictionary to diff.
      @param second:  Second dicationary to diff.
      @return diff:   Dict of Key => (first.val, second.val)
  """
  diff = {}
  # Check all keys in first dict
  for key in first.keys():
    if (not second.has_key(key)):
      diff[key] = (first[key], KEYNOTFOUND)
    elif (first[key] != second[key]):
      diff[key] = (first[key], second[key])
  # Check all keys in second dict to find missing
  for key in second.keys():
    if (not first.has_key(key)):
      diff[key] = (KEYNOTFOUND, second[key])
  return diff


# print "%d entries in lexicon" % len(lexicon.lexical_entries)
# print "%d examples in lexicon" % sum([len(entry.examples) for entry in lexicon.where("examplefrequency > 0")])

# print "%d unique lexemes in text" % len(set(list(itertools.chain.from_iterable(mb_lists))))

# print "%d examples in text" %  len(text.examples)

def find_duplicates():
  return True


def json_format_test():
  entry = lexicon.lexical_entries[0]
  print entry.examples[0].ft
  return entry.json_format()


def is_adding_duplicates():
  mbs_and_examples = text.mbs_and_examples()
  mbs = mbs_and_examples.keys()
  for entry in lexicon.lexical_entries:
    # If this entry appears in the example morphemes
    match = entry.appears_in(mbs)
    if match:
      # get the examples that have a morpheme (mb) of this entry
      match_examples = mbs_and_examples[match]
      # Loop over the examples that have this morpheme
      for match_example in match_examples:
        # Generate an Example Object that goes into the lexicon (probably need to namespace this)
        lex_example = Example(match_example.list())
        # Check if that example is in the lexical entry object already
        if not entry.contains_example(lex_example):
          # Add example to the liexical entry object
          entry.add_example(lex_example)
          # Increment examplefrequency
          entry.examplefrequency += 1

          # write_small_lexicon()
          # is_adding_duplicates()
          # print len(lexicon.where("examplefrequency > 100"))