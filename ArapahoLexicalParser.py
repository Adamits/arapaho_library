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

class ArapahoLexicalParser(object):
  def __init__(self):
    self.lexical_entries = []
    self.lexeme_and_example = {}
    self.allolexeme_and_example = {}
    self.json = {}

  def parse(self):
    with open(get_text_directory()) as data_file:
      arapaho_json = json.load(data_file)
      self.json = arapaho_json

    for lex_id, lex_entry in arapaho_json.items():
      # Instantiate a lexical entry of all the json at this lex_id
      lexical_entry = LexicalEntry({lex_id: lex_entry})
      self.lexical_entries.append(lexical_entry)
      self.lexeme_and_example[lexical_entry.lex] = lexical_entry
      for allolexeme in lexical_entry.allolexemes:
        self.allolexeme_and_example[allolexeme] = lexical_entry

  def where(self, query_string):
    # Need to copy the json in order to modify so that we can do a little
    # hack in order to solve the issue that object path does not return the key,
    # which is the lex_id for us.
    query_json = self.json.copy()
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

class JsonObject(object):

  def __init__(self, all_json):
    self.all_json = all_json

  def parent(self, parent_lexid):
    return all_json[parent_lexid] if all_json[parent_lexid] else None

# Represents a lexical entry in the lexicon.
# All attributes are the values of the json dict,
# or an array of classes that represent nested data such as 'derivations'
class LexicalEntry(JsonObject):
  def __init__(self, entry_json):
    self.json = entry_json
    try:
      self.lex_id = self.json.keys()[0] #lex id is the key
    except:
      self.lex_id = ""
    try:
      self.status = self.json[self.lex_id]["status"]
    except:
      self.status = ""
    try:
      self.sound = self.json[self.lex_id]["sound"]
    except:
      self.sound = ""
    try:
      self.language = self.json[self.lex_id]["language"]
    except:
      self.language = ""
    try:
      self.date_modified = self.json[self.lex_id]["date_modified"]
    except:
      self.date_modified = strftime("%Y-%m-%d %H:%M:%S")
    try:
      self.image = self.json[self.lex_id]["image"]
    except:
      self.image = ""
    try:
      self.gloss = self.json[self.lex_id]["gloss"]
    except:
      self.gloss = ""
    try:
      self.senses = [Sense(s) for s in self.json[self.lex_id]["senses"]]
    except:
      self.senses = []
    try:
      self.pos = self.json[self.lex_id]["pos"]
    except:
      self.pos = ""
    try:
      self.parent_lex = self.json[self.lex_id]["parent_lex"]
    except:
      self.parent_lex = ""
    try:
      self.morphology = self.json[self.lex_id]["morphology"]
    except:
      self.morphology = ""
    try:
      self.derivations = [Derivation(d) for d in self.json[self.lex_id]["derivations"]]
    except:
      []
    try:
      self.allolexemes = self.json[self.lex_id]["allolexemes"]
    except:
      self.allolexemes = []
    try:
      self.lex = self.json[self.lex_id]["lex"]
    except:
      self.lex = ""
    try:
      self.date_added = self.json[self.lex_id]["date_added"]
    except:
      self.date_added = strftime("%Y-%m-%d %H:%M:%S")
    try:
      self.base_form = self.json[self.lex_id]["base_form"]
    except:
      self.base_form = ""
    try:
      self.examplefrequency = self.json[self.lex_id]["examplefrequency"]
    except:
      self.examplefrequency = 0
    try:
      self.parent_lexid = self.json[self.lex_id]["parent_lexid"]
    except:
      self.parent_lexid = ""
    try:
      self.parent_rel = self.json[self.lex_id]["parent_rel"]
    except:
      self.parent_rel = ""
    try:
      self.examples = [Example(e) for e in self.json[self.lex_id]["examples"]]
    except:
      self.examples = []

#  def add_example(self, options={}):


class Derivation(JsonObject):
  def __init__(self, derivation_json):
    self.json  = derivation_json
    self.type  = self.json.keys()[0] # Always only one type per derivation
    self.value = self.json[self.type]

# Try multiple for senses, as there should always be a sense with the gloss as its definition
# This json is a list of dicts
class Sense(JsonObject):
  def __init__(self, sense_json):
    self.json       = sense_json
    self.definition = self.json.get("definition")
    self.usage      = self.json.get("usage")
    self.scientific = self.json.get("scientific")
    self.synonym    = self.json.get("synonym")
    self.sources    = self.json.get("sources")
    self.note       = self.json.get("note")
    self.example    = self.json.get("example")

class Example(JsonObject):
  def __init__(self, example_json):
    self.json = example_json
    self.ref  = self.json[0]
    self.tx   = self.json[1]
    self.mb   = self.json[2]
    self.ge   = self.json[3]
    self.ps   = self.json[4]
    self.ft   = self.json[5]

def test_parser():
  ap = ArapahoLexicalParser()
  ap.parse()
  return ap.lexical_entries
