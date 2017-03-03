import json
from time import strftime
from objectpath import *
import re

# Note that x= dict[key], where key points to another dict
# seems to store a pointer to that dict in python, so updating
# an attribute of a LexicalEntry SHOULD also update the json...

# Path to arapaho_lexicon.json
arapaho_json_path = "./data/arapaho_lexicon.json"

class ArapahoLexicalParser(object):
  def __init__(self):
    self.lexical_entries = []
    self.json = {}

  def parse(self):
    with open(arapaho_json_path) as data_file:
      arapaho_json = json.load(data_file)
      self.json = arapaho_json

    for lex_id, lex_entry in arapaho_json.items():
      # Instantiate a lexical entry of all the json at this lex_id
      self.lexical_entries.append(LexicalEntry({lex_id: lex_entry}))

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