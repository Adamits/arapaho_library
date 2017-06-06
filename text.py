# -*- coding: utf-8 -*-
from lexicon import *
import collections

# Note that x= dict[key], where key points to another dict
# seems to store a pointer to that dict in python, so updating
# an attribute of a LexicalEntry SHOULD also update the json...

class Text(object):
  def __init__(self):
    self.examples          = []
    self.refs              = []
    self.refs_and_examples = {}

  # For parsing the igt txt files that seem to be an output of toolbox
  def parse(self, text_path):
    # Get all lines from text, removing trailing whitespace
    lines = [line.strip() for line in codecs.open(text_path, encoding="Latin-1")]

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

      if re.match(r'\\ref', line):
        # When we hit a new ref, we need to store all of the data within that ref
        # I.e. before the next \ref, as a new TextExample
        if current_ref != "":
          # Instantiate TextExample with the current_ref
          text_example = TextExample()
          text_example.ref = current_ref

          # Add all of the lines of info to the TextExample.
          # Only set a value for the TextExample if there data to add
          if len(current_ref_dict["tx"]) > 0:
            text_example.tx = ' '.join(current_ref_dict["tx"])
          if len(current_ref_dict["mb"]) > 0:
            text_example.mb = ' '.join(current_ref_dict["mb"])
          if len(current_ref_dict["ge"]) > 0:
            text_example.ge = ' '.join(current_ref_dict["ge"])
          if len(current_ref_dict["ps"]) > 0:
            text_example.ps = ' '.join(current_ref_dict["ps"])
          if len(current_ref_dict["ft"]) > 0:
            text_example.ft = ' '.join(current_ref_dict["ft"])

          # Double check if there was actually example data in the example_block, or just noise
          # then add it to the list
          if text_example.contains_data():
            self.examples.append(text_example)
            self.refs_and_examples[text_example.ref].append(text_example)

        # Store the value of the ref, and remove trailing whitespace
        current_ref = re.split(r'\\ref', line)[1].strip()
        self.refs.append(current_ref)
        self.refs_and_examples[current_ref] = []
        current_ref_dict = {}
        current_ref_dict["tx"] = []
        current_ref_dict["mb"] = []
        current_ref_dict["ge"] = []
        current_ref_dict["ps"] = []
        current_ref_dict["ft"] = []
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

  def where(self, query_dict):
    match_examples = []
    for example in self.examples:
      example_dict = example.__dict__.copy()
      # Check if the query dict is in the example_dict
      if set(query_dict.items()).issubset(set(example_dict.items())):
        match_examples.append(example)

    return match_examples

  def mb_ps_tuples_and_examples(self):
    mb_ps_dict = {}
    for example in self.examples:
      for mb_ps in example.mb_and_ps_tuples():
        mb_ps_dict.setdefault(mb_ps, []).append(example)

    return mb_ps_dict

  def refs(self):
    return[text_example.ref for text_example in self.examples]

  def examples_as_dicts(self):
    return [example.dict_with_segmentation() for example in self.examples]

  def write(self, filename):
    with open(filename, 'w') as outfile:
      outfile.write('\n\n'.join([example.write_string() for example in self.examples]))

  #def concordance(self, input_lex, input_pos, window=5):


  def json_format(self):
    formatted_dict = {}

    for text_example in self.examples:
      formatted_dict.update(text_example.json_format())

    return formatted_dict

class TextExample(object):

  def __init__(self, options={}):
    self.ref = options.get("ref", "")
    self.tx = options.get("tx", "")
    self.mb = options.get("mb", "")
    self.ge = options.get("ge", "")
    self.ps = options.get("ps", "")
    self.ft = options.get("ft", "")
    self.id = options.get("_id", "")

  def list(self):
    return [self.ref, self.tx, self.mb, self.ge, self.ps, self.ft]

  def contains_data(self):
    return self.tx != "" or self.mb != "" or self.ge != "" or self.ps != "" or self.ft != ""

  def contains_ref(self):
    return self.ref != ""

  # Cleaned list of each morpheme of the mb string
  # This can be used to point a morpheme, which should correspond
  # with a lex, to all of the information for that example
  def get_mb_list(self):
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

  def mb_and_ps_tuples(self):
    return zip(self.get_mb_list(), self.get_ps_list())

  def get_segments(self):
    return [Segment(self, i, mb_and_ps_tup) for i, mb_and_ps_tup in enumerate(self.mb_and_ps_tuples())]

  def dict_with_segmentation(self):
    formatted_dict = self.__dict__.copy()
    formatted_dict.update({"mb_list": self.get_mb_list(), "ps_list": self.get_ps_list(), "ge_list": self.get_ge_list()})

    formatted_dict.update({"segments": []})
    for seg in self.get_segments():
      formatted_dict["segments"].append({"morpheme": seg.morpheme, "pos": seg.pos})

    return formatted_dict

  def write_string(self):
    return '\n'.join(["\%s %s" % (key, self.__dict__[key]) for key in ["ref", "tx", "mb", "ge", "ps", "ft"]])

  def json_format(self):
    formatted_dict = self.__dict__.copy()
    return {formatted_dict.pop("ref"): formatted_dict}


class Segment(object):

  def __init__(self, example, index, mb_ps_tup=()):
    self.morpheme = mb_ps_tup[0]
    self.pos = mb_ps_tup[1]
    self.example = example
    self.index = index

  def previous_segment(self):
    try:
      return self.example.get_segments()[self.index - 1]
    except:
      return "<s>"

  def next_segment(self):
    try:
      return self.example.get_segments()[self.index + 1]
    except:
      return "</s>"

def run_test():
  x = Text()
  x.parse()
