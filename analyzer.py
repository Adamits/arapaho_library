#  In here lets put all the methods that do analysis
# and possible updates tot he corpus and or lexicon

import collections

class Analyzer:

  def __init__(self, corpus):
    self.corpus = corpus
    self.log_string = ""

  def pos_counts_regex(self, regex):
    examples = self.corpus.get_text_examples({'segments.pos': {"$regex": regex}})

    print "%d examples have a pos that matches %s" % (len(examples), regex.pattern)
    self._log("%d examples have a pos that matches %s\n" % (len(examples), regex.pattern))

    matching_pos = [segment.pos for example in examples for segment in example.get_segments() if
                    regex.findall(segment.pos)]

    counts = collections.Counter(matching_pos)
    print "MATCHING TOKENS: %s" % counts.keys()
    print "%d matches on %s in the corpus" % (sum(counts.values()), regex.pattern)
    self._log("%d tokens match %s in the corpus\n" % (sum(counts.values()), regex.pattern))
    self._log("\n")

  def pos_counts_exact(self, search_string):
    stats = []
    examples = self.corpus.get_text_examples({'segments.pos': search_string})

    print "%d examples have the pos %s" % (len(examples), search_string)
    self._log("%d examples have the pos %s\n" % (len(examples), search_string))

    matching_pos = [segment.pos for example in examples for segment in example.get_segments() if
                    segment.pos == search_string]

    counts = collections.Counter(matching_pos)
    print "MATCHING TOKENS: %s" % counts.keys()
    print "%d total %s in the corpus" % (sum(counts.values()), search_string)
    self._log("%d tokens are exactly %s in the corpus\n" % (sum(counts.values()), search_string))
    self._log("\n")

  def _log(self, log_str):
    self.log_string += log_str

  def write(self, log_file_name):
    with open(log_file_name, 'w') as outfile:
      outfile.write(self.log_string)