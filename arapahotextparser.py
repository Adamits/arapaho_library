# -*- coding: utf-8 -*-
import json
from time import strftime
import re
import codecs

# Note that x= dict[key], where key points to another dict
# seems to store a pointer to that dict in python, so updating
# an attribute of a LexicalEntry SHOULD also update the json...

class ArapahoTextParser(object):
  def __init__(self):
    self.examples          = []
    self.refs              = []
    self.refs_and_examples = {}

  def parse(self, text_path):
    # Get all lines from text, removing trailing whitespace
    lines = [line.strip() for line in codecs.open(text_path, encoding='latin-1')]

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
        # When we hit a new ref, we need to store all of the examples that are within that ref
        if current_ref != "":
          # Loop over all lines under this ref, assume that if there is no tx,
          # then we do not need to instantiate it as an example.
          # Basically, len(current_ref_dict["tx"]) should = the number of examples from this ref
          for i in range(len(current_ref_dict["tx"])):
            text_example = TextExample()
            text_example.ref = current_ref
            if len(current_ref_dict["tx"]) > i:
              text_example.tx = current_ref_dict["tx"][i]
            if len(current_ref_dict["mb"]) > i:
              text_example.mb = current_ref_dict["mb"][i]
            if len(current_ref_dict["ge"]) > i:
              text_example.ge = current_ref_dict["ge"][i]
            if len(current_ref_dict["ps"]) > i:
              text_example.ps = current_ref_dict["ps"][i]
            if len(current_ref_dict["ft"]) > i:
              text_example.ft = current_ref_dict["ft"][i]
            # If we do not have an ft for this index, then use the last one of the ft slot.
            # It seems that the glosses in a ref should all be pointing to the same ft, but
            # we will check index and if not do last ft just to be safe.
            elif len(current_ref_dict["ft"]) > 0:
              text_example.ft = current_ref_dict["ft"][-1]
            # Double check if there was actually example data in the example_block, or just noise
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
      example_dict = example.__dict__
      # Check if the query dict is in the example_dict
      if set(query_dict.items()).issubset(set(example_dict.items())):
        match_examples.append(example)

    return match_examples

  def mbs_and_examples(self):
    mb_dict = {}
    for example in self.examples:
      for mb in example.get_mb_list():
        mb_dict.setdefault(mb, []).append(example)

    return mb_dict

  def to_json(self):
    return json.dumps(text_example.json() for text_example in self.examples)

    return all_data_dict

class TextExample(object):

  def __init__(self, options={}):
    self.ref = options.get("ref", "")
    self.tx = options.get("tx", "")
    self.mb = options.get("mb", "")
    self.ge = options.get("ge", "")
    self.ps = options.get("ps", "")
    self.ft = options.get("ft", "")

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
    mb_string = self.mb

    # Remove the space delimited '-' and put it in the list index
    # With the preceding string
    morphemes = re.split(r'\s+', mb_string)
    if '-' in morphemes:
      k = morphemes.index('-')
      morphemes[k - 1] = morphemes[k - 1].replace(morphemes[k - 1], morphemes[k - 1] + '-')
      morphemes.remove('-')

      mb_string = '  '.join(morphemes)

    # mb has no dashes and no '' and no ' '
    mb_list = re.split(r'\s+', mb_string)
    if '' in mb_list:
      mb_list.remove('')
    if ' ' in mb_list:
      mb_list.remove(' ')

    return mb_list

def run_test():
  x = ArapahoTextParser()
  x.parse()
