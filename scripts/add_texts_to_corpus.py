import os
import sys
import traceback
from utility_functions import add_texts_to_corpus as util
from arapaho_library import text as arapaho_text

data_dir = "/Users/ajwieme/arapaho-analysis/data/all_txt/"

from arapaho_library import corpus
ps_corpus = corpus.Corpus(corpus_name="ps_corpus")
ps_corpus.collection.remove()

failed = []
failed_count = 0

for root, dirs, files in os.walk(data_dir):
  for file in files:
    if file.endswith('.xml') or file.endswith('.txt'):
      t = arapaho_text.Text(root + file)
      try:
        print("Adding " + file + "...")
        # This will use the txt_parser, which is currently implemented to JUST
        # Add morpheme pos tags
        t.parse(root + file)
        util.add_texts_to_corpus(ps_corpus, [t])
      except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_traceback))
        failed_count += 1
        failed.append(file)

print("%i files failed: %s" % (failed_count, ", ".join(failed)))