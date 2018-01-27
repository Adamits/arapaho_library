import re
from arapaho_library import text

def get_text_examples(lines, text_object):
  text_examples = []
  current_ref = ""

  for line_index, line in enumerate(lines):
    # If the line does not start with \, then it is trailing text from the last line
    # so add it to that line in the dict, space padded
    if not line.startswith("\\") and line != '' and line_index > 0:
      last_line = lines[line_index - 1]
      if re.match(r'\\tx', last_line):
        current_ref_dict["tx"][-1] += " %s" % line
      elif re.match(r'\\mb', last_line):
        current_ref_dict["mb"][-1] += " %s" % line
      elif re.match(r'\\ge', last_line):
        current_ref_dict["ge"][-1] += " %s" % line
      elif re.match(r'\\ps', last_line):
        current_ref_dict["ps"][-1] += " %s" % line
      elif re.match(r'\\ft', last_line):
        current_ref_dict["ft"][-1] += " %s" % line
      elif re.match(r'\\ELANParticipant', last_line):
        # Only ever 1 participant per ref
        current_ref_dict["speaker"][-1] = line

    if re.match(r'\\ref', line):
      # When we hit a new ref, we need to store all of the data within that ref
      # I.e. before the next \ref, as a new TextExample
      if current_ref != "":
        # Instantiate TextExample with the current_ref
        text_example = text.TextExample()
        text_example.ref = current_ref
        text_example.text_id = current_ref.split('.')[0]

        # Aggregate each piece in the ref_dict to be single strings of all of the IGT info
        word_string = ""
        morphemes_string = ""
        gloss_string = ""
        pos_string = ""
        free_translation = ""
        speaker = ""
        if len(current_ref_dict["tx"]) > 0:
          word_string = ' '.join(current_ref_dict["tx"])
        if len(current_ref_dict["mb"]) > 0:
          morphemes_string = ' '.join(current_ref_dict["mb"])
        if len(current_ref_dict["ge"]) > 0:
          gloss_string = ' '.join(current_ref_dict["ge"])
        if len(current_ref_dict["ps"]) > 0:
          pos_string = ' '.join(current_ref_dict["ps"])
        if len(current_ref_dict["ft"]) > 0:
          free_translation = ' '.join(current_ref_dict["ft"])
        if len(current_ref_dict["speaker"]) > 0:
          # Only ever 1 'participant' speaker per ref
          speaker = current_ref_dict["speaker"]

        words = get_words(word_string)
        # just going to be populated with pos for now
        morphemes = get_morphemes(morphemes_string, pos_string, gloss_string)
        text_example.free_translation = free_translation
        # add the speaker to the line
        text_example.speaker = speaker

        # We are just going to add the 'morpheme' for now since we only care about the pos counts
        # for this project. Since they dont always align correctly with words even, we will just add blank strings for words
        if morphemes:
          text_examples.append(text_example)
          for word_morphemes in morphemes:
            t_word = text_example.add_word_segment("")
            [t_word.add_morpheme_segment(m) for m in word_morphemes]
        else:
          # In this case, the TextExample is not added
          print(current_ref + " does not have any pos (\ps) to parse!")

      # Store the value of the ref, and remove trailing whitespace
      current_ref = re.split(r'\\ref', line)[1].strip()
      current_ref_dict = {}
      current_ref_dict["tx"] = []
      current_ref_dict["mb"] = []
      current_ref_dict["ge"] = []
      current_ref_dict["ps"] = []
      current_ref_dict["ft"] = []
      current_ref_dict["speaker"] = ""
    elif re.match(r'\\tx', line):
      current_ref_dict["tx"].append(re.split(r'\\tx', line)[1].strip())
    elif re.match(r'\\mb', line):
      current_ref_dict["mb"].append(re.split(r'\\mb', line)[1].strip())
    elif re.match(r'\\ge', line):
      current_ref_dict["ge"].append(re.split(r'\\ge', line)[1].strip())
    elif re.match(r'\\ps', line):
      current_ref_dict["ps"].append(re.split(r'\\ps', line)[1].strip())
    elif re.match(r'\\ft', line):
      current_ref_dict["ft"].append(re.split(r'\\ft', line)[1].strip())
    elif re.match(r'\\ELANParticipant', line):
      # There should only be one speaker
      current_ref_dict["speaker"] = re.split(r'\\ELANParticipant', line)[1].strip()

  return text_examples

def get_words(text_string):
  return re.split(r'\s+', text_string)

def get_morphemes(morphemes_string, pos_string, gloss_string):
  """
  given strings of morpheme, pos, and gloss text from toolbox,
  return a list of dicts [{dict_that_morpheme_object can read in},{dict_that_morpheme_object can read in}, {etc}]
  """
  word_boundary_morpheme_string = ""
  word_boundary_pos_string = ""
  morphemes = re.split(r'\s+', morphemes_string)
  pos_list = re.split(r'\s+', pos_string)
  glosses = re.split(r'\s+', gloss_string)

  if len(pos_string) > 0:
    for i, p in enumerate(pos_list):
      # If it ends with a dash, then the next mb is part of the same word
      if p.endswith('-'):
        # Add it to the string, padded by whitespace unless this is the first word
        if i > 0:
          word_boundary_pos_string += " "
        word_boundary_pos_string += p[:-1]
      # If the segment itself is a dash, that means that the mb before and after it are in the same word
      elif p == '-':
        # Don't add it to the list, but go to the next one, and add that to the list
        # In the next iteration
        continue
      # Otherwise it is a different word
      else:
        # Add it to the string, padded by whitespace unless this is the first word
        if i > 0:
          word_boundary_pos_string += " "
        word_boundary_pos_string += p
        # If there is an upcoming isolated dash, go to it, otherwise, we have reached the end of the word
        try:
          if pos_list[i + 1] == "-":
            continue
          else:
            # Add '$' to mark a word boundary
            word_boundary_pos_string += " $"
        # The except would mean we have hit the end of the list
        except:
          continue

    # Split the word boundary strings, and zip them to get tuples of morphemes and pos list per word boundary
    words = word_boundary_pos_string.split(" $ ")
    return_words = []

    for word in words:
      morpheme_dicts = []
      for pos in re.split(r'\s+', word):
        morpheme_dicts.append({"pos": pos})

      return_words.append(morpheme_dicts)

    return return_words

"""
  #TODO: add glosses to this function.
  for i, m in enumerate(morphemes):
    # If it ends with a dash, then the next mb is part of the same word
    if m.endswith('-'):
      # Add it to the string, padded by whitespace unless this is the first word
      if i > 0:
        word_boundary_morpheme_string += " "
        word_boundary_pos_string += " "
      word_boundary_morpheme_string += m[:-1]
      word_boundary_pos_string += pos_list[i][:-1]
    # If the segment itself is a dash, that means that the mb before and after it are in the same word
    elif m == '-':
      # Don't add it to the list, but go to the next one, and add that to the list
      # In the next iteration
      continue
    # Otherwise it is a different word
    else:
      # Add it to the string, padded by whitespace unless this is the first word
      if i > 0:
        word_boundary_morpheme_string += " "
        word_boundary_pos_string += " "
      word_boundary_morpheme_string += m
      word_boundary_pos_string += pos_list[i]
      # If there is an upcoming isolated dash, go to it, otherwise, we have reached the end of the word
      try:
        if morphemes[i+1] == "-":
          continue
        else:
          # Add '$' to mark a word boundary
          word_boundary_morpheme_string += " $"
          word_boundary_pos_string += " $"
      # The except would mean we have hit the end of the list
      except:
        continue

  # Split the word boundary strings, and zip them to get tuples of morphemes and pos list per word boundary
  words = zip(word_boundary_morpheme_string.split(" $ "), word_boundary_pos_string.split(" $ "))
  return_words = []

  for word in words:
    morphemes, pos = word
    morpheme_dicts = []
    for m, p in zip(re.split(r'\s+', morphemes), re.split(r'\s+', pos)):
      morpheme_dicts.append({"morpheme": m, "pos": p})

    return_words.append(morpheme_dicts)

  return return_words
"""



'''
  from old text API:


  def get_mb_list(self):
      #IF INPUT WAS .txt
        #Cleaned list of each morpheme of the mb string
        #This can be used to point a morpheme, which should correspond
        #with a lex, to all of the information for that example
    # Remove the space delimited '-' and put it in the list index
    # With the preceding string
    mb_string = self.mb
    mb = re.split(r'\s+', mb_string)
    if '-' in mb:
      indices = [i for i, x in enumerate(mb) if x == '-']
      for k in indices:
        mb[k - 1] = mb[k - 1].replace(mb[k - 1], mb[k - 1] + '-')

      if '-' in mb:
        mb = [x for x in mb if x != '-']

      mb_string = '  '.join(mb)

    # Should have no dashes and no '' and no ' '
    mb_list = re.split(r'\s+', mb_string)
    if '' in mb_list:
      mb_list.remove('')
    if ' ' in mb_list:
      mb_list.remove(' ')
    return mb_list

  def get_ps_list(self):
    # Remove the space delimited '-' and put it in the list index
    # With the preceding string
    pos_string = self.ps
    clean_pos_list = []
    # Remove - and lowercase to match on lexical entries
    for pos in re.split(r'\s+', pos_string):
      clean_pos = pos.replace("-", '')
      clean_pos_list.append(clean_pos)

    if '' in clean_pos_list:
      clean_pos_list = [x for x in clean_pos_list if x != '']
    if ' ' in clean_pos_list:
      clean_pos_list = [x for x in clean_pos_list if x != ' ']

    return clean_pos_list

  def get_ge_list(self):
    mb_list = self.get_mb_list()
    target_length = len(mb_list)
    # Remove the space delimited '-' and put it in the list index
    # With the preceding string
    ge_string = self.ge
    clean_ge_list = []
    # Remove - and lowercase to match on lexical entries
    for ge in re.split(r'\s+', ge_string):
      clean_ge = ge.replace("-", "")
      clean_ge_list.append(clean_ge)

    if '' in clean_ge_list:
      clean_ge_list.remove('')
    if ' ' in clean_ge_list:
      clean_ge_list.remove(' ')

    return clean_ge_list
'''