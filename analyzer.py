#  In here lets put all the methods that do analysis
# and possible updates tot he corpus and or lexicon

import collections

class Analyzer:

  def __init__(self, corpus):
    self.corpus = corpus
    self.log_string = ""

  def log_totals(self):
    segment_cursor = self.corpus.collection.find({}, {"segments.pos": 1, "_id": 0})
    total_examples = segment_cursor.count()
    total_pos = len([segment["pos"] for dict in segment_cursor for segment in dict["segments"]])

    self._log("%d total examples in the corpus\n" % total_examples)
    self._log("%d total tokens in the corpus\n\n" % total_pos)

  def pos_counts_regex(self, regex):
    examples = self.corpus.get_text_examples({'segments.pos': {"$regex": regex}})

    segment_cursor = self.corpus.collection.find({}, {"segments.pos": 1, "_id": 0})
    total_examples = segment_cursor.count()
    total_pos = len([segment["pos"] for dict in segment_cursor for segment in dict["segments"]])

    self._log("%d examples have a pos that matches %s, representing %.1f%% of examples\n" % (
              len(examples), regex.pattern, float(len(examples)) / float(total_examples) * 100.0))

    matching_pos = [segment.pos for example in examples for segment in example.get_segments() if
                    regex.findall(segment.pos)]

    counts = collections.Counter(matching_pos)
    print "MATCHING TOKENS: %s" % counts.keys()
    print "%d matches on %s in the corpus" % (sum(counts.values()), regex.pattern)
    self._log("%d tokens match %s in the corpus, representing %.1f%% of the corpus\n" % (
    sum(counts.values()), regex.pattern, float(sum(counts.values())) / float(total_pos) * 100.0))
    self._log("\n")

  def pos_counts_exact(self, search_string):
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

  def all_pos_counts(self):
    segment_cursor = self.corpus.collection.find({}, {"segments.pos": 1, "_id": 0})
    total_examples = segment_cursor.count()
    all_pos = [segment["pos"] for dict in segment_cursor for segment in dict["segments"]]

    total_pos = len(all_pos)
    pos_counts = collections.Counter(all_pos).most_common()

    print "%d tokens across %d examples in the corpus" % (total_pos, total_examples)
    self._log("%d tokens across %d examples in the corpus\n\n" % (total_pos, total_examples))
    self._log("%d unique parts of speech in this corpus\n\n" % (len(pos_counts)))

    for pos, pos_count in pos_counts:
      example_count = self.corpus.get_cursor({'segments.pos': pos}).count()
      self._log("%d examples have the pos %s, representing %d%% of examples\n"
                % (example_count, pos, round(float(example_count) / float(total_examples), 2) * 100))
      self._log("%d total %s in the corpus, representing %d%% of the corpus\n"
                % (pos_count, pos, round(float(pos_count) / float(total_pos), 2) * 100))
      self._log("\n")


  def _log(self, log_str):
    self.log_string += log_str

  def write(self, log_file_name):
    with open(log_file_name, 'w') as outfile:
      outfile.write(self.log_string)