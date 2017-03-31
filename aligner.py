# Right now this class is solely for the purpose of solving lookup issues
# Wherein it is difficult to store the correct segment of the ge (gloss) tier
# of these annotated texts because multiple English words can represent a single
# Arapaho morpheme, and the ge's are represented space delimited, so we have no way
# of knowing how many words of the gloss map to a single morpheme.

# -*- coding: utf-8 -*-
import re

class Aligner(object):
  def __init__(self, input_text, input_lexicon):
    self.text = input_text
    self.lexicon = input_lexicon

  def align(self, new_text_file, log_file):
    log_string = ""

    for text_example in self.text.examples:
      # Get the clean lits of relevant info
      mb_list, ps_list, ge_list = text_example.get_mb_list(), text_example.get_ps_list(), text_example.get_ge_list()
      # If everything aligns, were good
      if len(ge_list) == len(mb_list):
        continue
      # Otherwise, we know that the gloss must have more tokens than the mb and ps tiers
      else:
        # Look over the tuples of mb_ps
        for mb_ps in text_example.mb_and_ps_tuples():
          # get the index of the mb in the list
          mb_index = mb_list.index(mb_ps[0])
          # find lexical entries that match the mb
          if self.lexicon.lexes_and_lexical_entries.get(mb_ps[0]):
            for entry in self.lexicon.find_by_lex(mb_ps[0]):
              # Check that the pos matches too
              if entry.pos == mb_ps[1]:
                # Get th number of tokens in the leixcal entry's gloss
                gloss_length = len(re.split(r'\s+', entry.gloss))
                # If its >1, it needs to be annotated differently for realignment
                if gloss_length > 1:
                  # Get a string starting at the mb-aligned gloss, of length n where n is the
                  # length of the entry gloss
                  aligned_gloss = ' '.join(ge_list[mb_index:mb_index + gloss_length])
                  # If this matches the entry gloss, then:
                  # A: this instance of the mb must be a reference to the lexical entry and
                  # B: aligned_gloss must be the full gloss of this mb, and therefore we can
                  # change it to be (.) delimited rather than space delimited.
                  if aligned_gloss == entry.gloss:
                    # change the ge so that all isntances of aligned gloss are replaced by (.) delimited version
                    # of aligned_gloss
                    text_example.ge = text_example.ge.replace(aligned_gloss, '.'.join(re.split(r'\s+', aligned_gloss)))
                  else:
                    print entry.lex_and_allolex_list()
                    print aligned_gloss
                    print entry.gloss
                    print "==========="
          else:
            log_string += "%s is not in the lexicon! \n\n" % ','.join(mb_ps)

      self.text.write(new_text_file)

      with open(log_file, 'w') as outfile:
        outfile.write(log_string)
