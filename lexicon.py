# -*- coding: utf-8 -*-
import json
import codecs
from time import strftime
from objectpath import *
import re


# Note that x= dict[key], where key points to another dict
# seems to store a pointer to that dict in python, so updating
# an attribute of a LexicalEntry SHOULD also update the json...
class JsonObject(object):
  def json_format(self):
    return self.__dict__

class Lexicon(JsonObject):
  def __init__(self):
    self.lexical_entries = []
    self.lexes_and_lexical_entries = {}
    self.json_dict = {}

  def parse(self, lexicon_path):
    with codecs.open(lexicon_path, encoding='utf-8') as data_file:
      arapaho_json = json.load(data_file)
      self.json_dict = arapaho_json

    for lex_id, lex_entry in arapaho_json.items():
      # Instantiate a lexical entry of all the json at this lex_id
      lexical_entry = LexicalEntry({lex_id: lex_entry})
      # Add lex/allolex as keys and/or append entry to that key
      self.lexes_and_lexical_entries.setdefault(lexical_entry.lex, []).append(lexical_entry)
      for allolex in lexical_entry.allolexemes:
        self.lexes_and_lexical_entries.setdefault(allolex, []).append(lexical_entry)
      self.lexical_entries.append(lexical_entry)

  def find_by_lex(self, lex):
    return self.lexes_and_lexical_entries.get(lex, [])

  # Note that this queries the json read in by the parser
  # Which means that after entries are updated, this will still be querying the
  # JSON originally fed into the parser until the json_dict attribute is updated.
  def where(self, query_string):
    # Need to copy the json in order to modify so that we can do a little
    # hack in order to solve the issue that object path does not return the key,
    # which is the lex_id for us.
    # TODO figure out a way to still point to the original json_dict,
    # TODO so that we can update the json that will ultimately write to a file
    # TODO without adding new lex_id keys for the hack explained above.
    query_json = self.json_dict.copy()
    # Add lex_id as a key in the dict so that it can be added back
    # as the highest level key so that instantiation of LexicalEntry objects will work.
    for lex_id in query_json.keys():
      query_json[lex_id].update({"lex_id": lex_id})
    # objectpath tree of json formatted for the query
    tree = Tree(query_json)
    # Use objectpath to get a generator of entries
    # where that matches objectpath query in query_string
    q = tree.execute("$..*[@.%s]" % query_string)
    # Convert generator to a list, loop over it, and instantiate LexicalEntry
    # objects with each one that returned
    lex_entries = []
    for lex_entry in list(q):
      # Add the lex_id as the key again, and remove it from the dict within
      lex_entries.append(LexicalEntry({lex_entry.pop("lex_id"): lex_entry}))

    return lex_entries

  def json_format(self):
    formatted_dict = {}
    for entry in self.lexical_entries:
      formatted_dict.update(entry.json_format())

    return formatted_dict

  def remove_all_entry_examples(self):
    [entry.remove_examples() for entry in self.lexical_entries]

# Represents a lexical entry in the lexicon.
# All attributes are the values of the json dict,
# or an array of classes that represent nested data such as 'derivations'
class LexicalEntry(JsonObject):
  def __init__(self, entry_json_dict):
    self.json_dict = entry_json_dict
    try:
      self.lex_id = self.json_dict.keys()[0]  # lex id is the key
    except:
      self.lex_id = ""
    try:
      self.status = self.json_dict[self.lex_id]["status"]
    except:
      self.status = ""
    try:
      self.sound = self.json_dict[self.lex_id]["sound"]
    except:
      self.sound = ""
    try:
      self.language = self.json_dict[self.lex_id]["language"]
    except:
      self.language = ""
    try:
      self.date_modified = self.json_dict[self.lex_id]["date_modified"]
    except:
      self.date_modified = strftime("%Y-%m-%d %H:%M:%S")
    try:
      self.image = self.json_dict[self.lex_id]["image"]
    except:
      self.image = ""
    try:
      self.gloss = self.json_dict[self.lex_id]["gloss"]
    except:
      self.gloss = ""
    try:
      self.semantic_domain = self.json_dict[self.lex_id]["semantic_domain"]
    except:
      self.semantic_domain = ""
    try:
      self.cultural = self.json_dict[self.lex_id]["cultural"]
    except:
      self.cultural = ""
    try:
      self.literal = self.json_dict[self.lex_id]["literal"]
    except:
      self.literal = ""
    try:
      self.user = self.json_dict[self.lex_id]["user"]
    except:
      self.user = ""
    try:
      self.etymology = self.json_dict[self.lex_id]["etymology"]
    except:
      self.etymology = ""
    try:
      self.usage_main = self.json_dict[self.lex_id]["usage_main"]
    except:
      self.usage_main = ""
    try:
      self.senses = [Sense(s) for s in self.json_dict[self.lex_id]["senses"]]
    except:
      self.senses = []
    try:
      self.pos = self.json_dict[self.lex_id]["pos"]
    except:
      self.pos = ""
    try:
      self.parent_lex = self.json_dict[self.lex_id]["parent_lex"]
    except:
      self.parent_lex = ""
    try:
      self.morphology = self.json_dict[self.lex_id]["morphology"]
    except:
      self.morphology = ""
    try:
      self.derivations = [Derivation(d) for d in self.json_dict[self.lex_id]["derivations"]]
    except:
      self.derivations = []
    try:
      self.allolexemes = self.json_dict[self.lex_id]["allolexemes"]
      # If it was not stored as a list, make it one
      if not isinstance(self.allolexemes, list):
        self.allolexemes = [self.allolexemes]
    except:
      self.allolexemes = []
    try:
      self.lex = self.json_dict[self.lex_id]["lex"]
    except:
      self.lex = ""
    try:
      self.date_added = self.json_dict[self.lex_id]["date_added"]
    except:
      self.date_added = strftime("%Y-%m-%d %H:%M:%S")
    try:
      self.base_form = self.json_dict[self.lex_id]["base_form"]
    except:
      self.base_form = ""
    try:
      self.examplefrequency = self.json_dict[self.lex_id]["examplefrequency"]
    except:
      self.json_dict[self.lex_id]["examplefrequency"] = 0
      self.examplefrequency = 0
    try:
      self.parent_lexid = self.json_dict[self.lex_id]["parent_lexid"]
    except:
      self.parent_lexid = ""
    try:
      self.parent_rel = self.json_dict[self.lex_id]["parent_rel"]
    except:
      self.parent_rel = ""
    try:
      self.examples = [Example(e) for e in self.json_dict[self.lex_id]["examples"]]
    except:
      self.json_dict[self.lex_id]["examples"] = []
      self.examples = []

  def lex_and_allolex_list(self):
    matching_lexemes = self.allolexemes[:]
    matching_lexemes.append(self.lex)

    return matching_lexemes

  # Returns a list of (ps, mb) tuples from the list of
  # (ps, mb) tuples that this entry appears in
  def get_match_from(self, comparison_list=[]):
    matching_lexemes = []

    for lexeme in self.lex_and_allolex_list():
      entry_tuple = (lexeme, self.pos)
      if entry_tuple in comparison_list:
        matching_lexemes.append(entry_tuple)

    return matching_lexemes

  def contains_example(self, input_example):
    for example in self.examples:
      if set(input_example.json_format()) == set(example.json_format()):
        return True

  def add_example(self, input_example):
    self.examples.append(input_example)

  def remove_examples(self):
    self.examples = []
    self.examplefrequency = 0

  def frequency_in_example_morphemes(self, example_morphemes_list):
    return sum([example_morphemes_list.count(x) for x in set(self.lex_and_allolex_list())])

  # Returns all refs for examples it occurs in
  def refs(self):
    return [example.ref for example in self.examples]

  def json_format(self):
    formatted_dict = self.__dict__.copy()
    formatted_dict.pop("json_dict")

    for key, val in formatted_dict.items():
      if isinstance(val, list) and len(val) > 0:
        if isinstance(val[0], JsonObject):
          formatted_dict[key] = [obj.json_format() for obj in formatted_dict[key]]

    return {formatted_dict.pop("lex_id"): formatted_dict}

# def add_example(self, options={}):


class Derivation(JsonObject):
  def __init__(self, derivation_json):
    self.json_dict = derivation_json
    self.type = self.json_dict.keys()[0]  # Always only one type per derivation
    self.value = self.json_dict[self.type]

  def json_format(self):
    formatted_dict = self.__dict__.copy()
    formatted_dict.pop("json_dict")

    return {formatted_dict["type"]: formatted_dict["value"]}


# Try multiple for senses, as there should always be a sense with the gloss as its definition
# This json is a list of dicts
class Sense(JsonObject):
  def __init__(self, sense_json):
    self.json_dict = sense_json
    self.definition = self.json_dict.get("definition")
    self.usage = self.json_dict.get("usage")
    self.scientific = self.json_dict.get("scientific")
    self.synonym = self.json_dict.get("synonym")
    self.sources = self.json_dict.get("sources")
    self.note = self.json_dict.get("note")
    self.example = self.json_dict.get("example")

  def json_format(self):
    formatted_dict = self.__dict__.copy()
    formatted_dict.pop("json_dict")
    for key in formatted_dict.keys():
      if formatted_dict[key] == None or formatted_dict[key] == "":
        formatted_dict.pop(key)

    return formatted_dict


class Example(JsonObject):
  def __init__(self, input_list):
    self.json_list = input_list
    self.ref = self.json_list[0]
    self.tx = self.json_list[1]
    self.mb = self.json_list[2]
    self.ge = self.json_list[3]
    self.ps = self.json_list[4]
    self.ft = self.json_list[5]

  def json_format(self):
    return [self.ref, self.tx, self.mb, self.ge, self.ps, self.ft if not isinstance(self.ft, list) else self.ft[0]]
    # Added bandage to self. because right now some are arbitrarily 1d arrays instead of string
    # Which can break stuff downstream


def test_parser():
  ap = Lexicon()
  ap.parse()
  return ap.lexical_entries
