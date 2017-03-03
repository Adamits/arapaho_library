# -*- coding: utf-8 -*-
__author__ = ['ghamzak', 'adam.wiemerslage']

import re
import json, codecs
from ArapahoParser import ArapahoParser

# Read in .txt of IGT
input_text = './data/master_text.txt'
arapaho_lexicon = "./data/arapaho_lexicon.json"
glossed_text = ""

with open(input_text, 'r') as f:
  text = f.readlines()   #213262
textcopy = text

# Store as a string with just the IGT keys that we care about
for i in range(len(textcopy)-1):
  if re.match(r'\\ref', textcopy[i]) or re.match(r'\\tx', textcopy[i]) or re.match(r'\\mb', textcopy[i]) or re.match(r'\\ge', textcopy[i]) or re.match(r'\\ps', textcopy[i]) or re.match(r'\\ft', textcopy[i]):
    glossed_text += textcopy[i]

# Split into a list of separate \\refs
glossed_text_list = re.split(r'\\ref ', glossed_text)
# Split into su-arrays by line within the \\ref
glossed_text_list = [re.split(r'\r\n', i) for i in glossed_text_list]
# Clean the data
for i in glossed_text_list:
  i.remove('')
glossed_text_list.remove(['']) if [''] in glossed_text_list else glossed_text_list
glossed_text_list.remove([]) if [] in glossed_text_list else glossed_text_list

# Put the entries in a dict of the format
# {\\ref : {tx : val, mb : val, etc...}}
glossed_text_dict = {}
for i in range(len(glossed_text_list)):   #24203
  glossed_text_dict[glossed_text_list[i][0]] = {}
  glossed_text_dict[glossed_text_list[i][0]]['tx'] = []
  glossed_text_dict[glossed_text_list[i][0]]['mb'] = []
  glossed_text_dict[glossed_text_list[i][0]]['ge'] = []
  glossed_text_dict[glossed_text_list[i][0]]['ps'] = []
  glossed_text_dict[glossed_text_list[i][0]]['ft'] = []
  for j in range(len(glossed_text_list[i])):
    if j > 0:
      if re.match(r'\\tx(?=.+)', glossed_text_list[i][j]):
        glossed_text_dict[glossed_text_list[i][0]]['tx'].append(glossed_text_list[i][j])
      if re.match(r'\\mb', glossed_text_list[i][j]):
        glossed_text_dict[glossed_text_list[i][0]]['mb'].append(glossed_text_list[i][j])
      if re.match(r'\\ge', glossed_text_list[i][j]):
        glossed_text_dict[glossed_text_list[i][0]]['ge'].append(glossed_text_list[i][j])
      if re.match(r'\\ps', glossed_text_list[i][j]):
        glossed_text_dict[glossed_text_list[i][0]]['ps'].append(glossed_text_list[i][j])
      if re.match(r'\\ft', glossed_text_list[i][j]):
        glossed_text_dict[glossed_text_list[i][0]]['ft'].append(glossed_text_list[i][j])

# Remove the space delimited '-' and put it in the list index
# With the preceding string
for i in glossed_text_dict.items():
  mb = i[1]['mb']
  for j in range(len(mb)):
    mid = re.split(r'\s+', mb[j])
    if '-' in mid:
      k = mid.index('-')
      mid[k-1] = mid[k-1].replace(mid[k-1], mid[k-1]+'-')
      mid.remove('-')

    mb[j] = '  '.join(mid)

  # print(mb)
  glossed_text_dict[i[0]]['mb'] = mb

# This has no dashes and no '' and no ' '
mblist = []
mbdict = {}
for i in glossed_text_dict.values():
  for j in i['mb']:
    a = re.split(r'\s+', j)
    if '' in a:
      a.remove('')
    if ' ' in a:
      a.remove(' ')
    for x in a:
      if x not in mblist and x != '':
        mblist.append(x)

# Instantiate a list at each mb slot
for i in mblist:
  mbdict[i] = []

for text_line in glossed_text_dict.items():
  for j in text_line[1]['mb']:
    a = re.split(r'\s+', j)
    if '' in a:
      a.remove('')
    if ' ' in a:
      a.remove(' ')
    for k in a:
      if k != '\\mb':
        mbdict[k].append(i[0])

mbdict.pop('\\mb')  # now len(mbdict) = 15417
mblist.remove('') if '' in mblist else '' #16351
# mblist.remove(' ')

# Use arapaho_library parser
parser = ArapahoParser()
parser.parse()

# Dicts of the form {lexeme: lex_id}
lexlexid = {}  #25531
allolexlexid = {}  #16286
for lexical_entry in parser.lexical_entries:
  # lexlexid[i[1]['lex']] = i[0]
  lexlexid[lexical_entry.lex_id] = lexical_entry.lex

  if len(lexical_entry.allolexemes) > 0:
    allolexlexid[lexical_entry].lex_id = lexical_entry.allolexemes

# now we have three useful dictionaries:
# one with all morphemes in the corpus with reference to their ref (called mbdict)
# one with mapping of all lexemes to their lexids in the json file (called lexlexid)
# one with mapping of all allolexemes to the lexid of their parent lexeme in the json file (called allolexlexid)
# now we should search the first one in its keys, find morphemes, and ask if that morpheme is in either lexlexid keys or allolexlexid keys.
# this way we'll find the lexid for that and we'll map examples to lexids
# now we should also have a dict that maps refs to whole examples > that's glossed_text_dict > so we have it all


# Looks like this instantiates dict of {ref: [ref]}
# Then it adds to the list all the other important keys from the IGT
# Let's do it smarter...
glossed_text_items = {}
for i in glossed_text_dict.items():
  ref = i[0]
  # Let's build a dict of {ref: {tx: the value of tx, mb: the value of mb, etc}
  glossed_text_items[ref] = {}
  for j in range(len(i[1]['tx'])):
    if i[1]['tx']:
      if len(i[1]['tx']) > j: #Check if index is in range
        glossed_text_items[i[0]].append(i[1]['tx'][j])
    if i[1]['mb']:
      if len(i[1]['mb']) > j:
        glossed_text_items[i[0]].append(i[1]['mb'][j])
    if i[1]['ge']:
      if len(i[1]['ge']) > j:
        glossed_text_items[i[0]].append(i[1]['ge'][j])
    if i[1]['ps']:
      if len(i[1]['ps']) > j:
        glossed_text_items[i[0]].append(i[1]['ps'][j])
  if i[1]['ft']:
    glossed_text_items[i[0]].append(i[1]['ft']) #this is a list which could be empty
  # except:
  #     print("mismatch in ref ")
  #     print(i[0])


# This maps each mb to all its examples in the dict. since it contains all the examples for each mb,
# it can safely count all, so we have examplefrequency as well.
mbtoprintall = {}
for i in mbdict.items():
  mbtoprintall[i[0]] = []
  for j in i[1]:  # j is the ref
    mbtoprintall[i[0]].append(prettyprintitems[j])

for i in mbtoprintall.items():
  desiredlex = []
  desiredlex.append(i[0])
  desiredlex.append(i[0]+'-')
  desiredlex.append(i[0]+' IC')
  desiredlex.append(i[0]+'- IC')
  desiredids = []
  # Store a list of the lexids associated with the mb
  for d in desiredlex:
    if d in lexlexid.values():
      ind = lexlexid.values().index(d)
      desiredid = lexlexid.keys()[ind]
      desiredids.append(desiredid)
    for v in allolexlexid.values():
      if d in v:
        ind2 = allolexlexid.values().index(v)
        desiredids.append(allolexlexid.keys()[ind2])
  # Loop over the ids, and at each id, append the example for that morpheme
  if desiredids:
    for j in desiredids:
      if isinstance(i[1], list):
        if len(i[1]) == 1:
          data[j]['examples'].append(i[1][0])
          data[j]['examplefrequency'] += 1
        # If morpheme occurs in multiple examples
        # Append each of those examples
        elif len(i[1]) > 1:# and i[1][1] and not re.match(r'\\tx', i[1][1]):
          for b in i[1]:
            if isinstance(b, list):# and not re.match(r'\\tx', b[1]):
              if len(b) > 1 and re.match(r'\\tx', b[1]):
                data[j]['examples'].append(b)
                data[j]['examplefrequency'] += 1
              elif b and b[1] and not re.match(r'\\tx', b[1]):
                for c in b:
                  data[j]['examples'].append(c)
                  data[j]['examplefrequency'] += 1

            # else:
            #     data[j]['examples'].append(b)
            #     data[j]['examplefrequency'] += 1
        # else:
        #     data[j]['examples'].append(i[1])
        #     data[j]['examplefrequency'] += 1


      # data[j]['examples'].append(i[1])
      # data[j]['examplefrequency'] = len(i[1])


def findlex(lex):
  for i in data.items():
    if i[1]['lex'] == lex:
      return i[0]

def findallolex(allolex):
  for i in data.items():
    if 'allolexemes' in i[1].keys():
      if i[1]['allolexemes']:
        if allolex in i[1]['allolexemes']:
          return i[0]

def findex(lex):
  return data[findlex(lex)]['examples']

with open(arapaho_lexicon, 'w') as outfile:
  json.dump(data, outfile)