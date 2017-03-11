# -*- coding: utf-8 -*-
import json
from time import strftime
from objectpath import *
import re


# Note that x= dict[key], where key points to another dict
# seems to store a pointer to that dict in python, so updating
# an attribute of a LexicalEntry SHOULD also update the json...

# Path to arapaho_lexicon.json
def get_text_directory():
  for line in open('config.txt'):
    if line.startswith('lexicon_path'):
      return line.split('=')[1].strip()
  exit('WARNING: could not find a value for lexicon_path')

class JsonObject(object):
  def __init__(self, json_dict):
    self.json_dict = json_dict

  def as_json_dict(self):
    return self.__dict__

class ArapahoLexicalParser(JsonObject):
  def __init__(self):
    self.lexical_entries = []
    self.json_dict = {}

  def parse(self):
    with open(get_text_directory()) as data_file:
      arapaho_json = json.load(data_file)
      self.json_dict = arapaho_json

    for lex_id, lex_entry in arapaho_json.items():
      # Instantiate a lexical entry of all the json at this lex_id
      lexical_entry = LexicalEntry({lex_id: lex_entry})
      self.lexical_entries.append(lexical_entry)

  def where(self, query_string):
    # Need to copy the json in order to modify so that we can do a little
    # hack in order to solve the issue that object path does not return the key,
    # which is the lex_id for us.
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

  def as_json_dict(self):
    formatted_dict = {}
    for entry in self.lexical_entries:
      formatted_dict.update(entry.as_json_dict())

    return formatted_dict

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
      []
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

  def appears_as(self):
    matching_lexemes = self.allolexemes
    matching_lexemes.append(self.lex)

    return matching_lexemes

  def appears_in(self, comparison_list=[]):
    for lexeme in self.appears_as():
      if lexeme in comparison_list:
        return lexeme

  def contains_example(self, input_example):
    for example in self.examples:
      if input_example.as_json_dict() == example.as_json_dict():
        return True

  def as_json_dict(self):
    formatted_dict = self.__dict__.copy()
    formatted_dict.pop("json_dict")

    for key, val in formatted_dict.items():
      if isinstance(val, list) and len(val) > 0:
        if isinstance(val[0], JsonObject):
          formatted_dict[key] = [obj.as_json_dict() for obj in formatted_dict[key]]

    return {formatted_dict.pop("lex_id"): formatted_dict}

#  def as_json_dict(self):
#    nested_dict = self.__dict__
#    for key, val in nested_dict:
#
#    {self.lex_id: {}}


# def add_example(self, options={}):


class Derivation(JsonObject):
  def __init__(self, derivation_json):
    self.json_dict = derivation_json
    self.type = self.json_dict.keys()[0]  # Always only one type per derivation
    self.value = self.json_dict[self.type]

  def as_json_dict(self):
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

  def as_json_dict(self):
    formatted_dict = self.__dict__.copy()
    formatted_dict.pop("json_dict")
    for key in formatted_dict.keys():
      if formatted_dict[key] == None:
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

  def as_json_dict(self):
    return [self.ref, self.tx, self.mb, self.ge, self.ps, self.ft]


def test_parser():
  ap = ArapahoLexicalParser()
  ap.parse()
  return ap.lexical_entries
