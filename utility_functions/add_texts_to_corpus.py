"""
INPUT: Text object, which contains many TextExamples, and the corpus object to add to
of IGT. Add these to the corpus of examples, which is
implemented as a mongodb.
"""

def add_texts_to_corpus(c, texts=[]):
  # Add the new texts, flattening the list to get all texts that a single "Text" object comrpises
  for t in texts:
    for t_id in t.json_format():
      c.add_entries([t_id])

  return c