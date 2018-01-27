# -*- coding: utf-8 -*-
from corpus import *
import re

corpus = Corpus()
regex = re.compile(r"\bvia.*")
verb_examples = corpus.get_text_examples({'segments.pos': {"$regex": regex}})
print([e.word_segments for e in verb_examples])
matching_segs = [segment for example in verb_examples for segment in example.word_segments if
                regex.findall(segment.pos)]
verb_counts = collections.Counter([matching_seg.pos for matching_seg in matching_segs])
mb_counts = collections.Counter([(matching_seg.pos, matching_seg.morpheme) for matching_seg in matching_segs])

counts_log = "FORMAT OF:\n pos: frequency\n\t most_frequent_morpheme for that pos: frequency of instances of morpheme with that pos\n\n\n"
for v in verb_counts.most_common():
  counts_log += "%s: %d\n" % (v[0], v[1])
  for mb_count in mb_counts.most_common():
    if mb_count[0][0] == v[0]:
      counts_log += "\t%s: %d\n\n" % (mb_count[0][1], mb_count[1])
      break

counts_file = codecs.open("./util_data/via.txt", "w", "utf-8")
counts_file.write(counts_log)
counts_file.close()

#examples = corpus.get_all_text_examples()

#print len(examples)

'''
#log_file = '\n'.join(["%s\n%s\n%s\n" % (example.tx, example.get_mb_list(), example.get_ps_list()) for example in examples])
log_file = ""
for example in examples:
  log_file += '\n' + '\n'.join(["%s\t%s" % (segment.morpheme, segment.pos) for segment in example.get_segments()])

file = codecs.open("./util_data/explore.txt", "w", "utf-8")
file.write(log_file)
file.close()
'''