import codecs
from collections import Counter
import re

toolbox_dictionary = "/Users/ajwieme/arapaho_library/data/Dictionary.txt"

# first line is some ID
first_line = [line.strip() for line in codecs.open(toolbox_dictionary, encoding="Latin-1")][0]
groups = '_'.join([line.strip() for line in codecs.open(toolbox_dictionary, encoding="Latin-1")][1:]).split("__")
group_dicts = []
dot_delimited_tags = Counter()
for group in groups:
  lines = group.split("_")

  # get a dict of each labe: value, and lowercase all the values
  group_dict = {}

  for l in group.split("_"):
    if len(l.split()) > 1:
      label, value = [l.split()[0], ' '.join(l.split()[1:])]
    else:
      label, value = (l, "")

    group_dict[label] = value

  group_dict["\\ps"] = group_dict.get("\\ps", "").lower()
  # remove .-delimitation for this speciic tag
  if re.match("(.*pass\.perf.*)", group_dict.get("\\ps", "")):
    group_dict["\\ps"] = group_dict["\\ps"].replace("pass.perf", "passperf")
  elif re.match("(.*pass\.imperf.*)", group_dict.get("\\ps", "")):
    group_dict["\\ps"] = group_dict["\\ps"].replace("pass.imperf", "passimperf")

  if "." in group_dict.get("\\ps", ""):
    tag = group_dict.get("\\ps")
    dot_delimited_tags[tag] += 1

  group_dicts.append(group_dict)

tag_groups = []
tags = list(dot_delimited_tags.keys())
for tag in tags:
  tag_group = [(tag, dot_delimited_tags[tag])]
  tags.pop(tags.index(tag))
  for other_tag in tags:
    if set(tag.split(".")) == set(other_tag.split(".")) and tag.split(".") != other_tag.split("."):
      tag_group.append((other_tag, dot_delimited_tags[other_tag]))
      tags.pop(tags.index(other_tag))

  tag_groups.append(tag_group)

for tag_group in tag_groups:
  if len(tag_group) > 1:
    gold_tag = sorted([(b, a) for a, b in tag_group], reverse=1)[0][1]
    for tag_tup in tag_group:
      tag = tag_tup[0]
      for group_dict in [g for g in group_dicts if g["\\ps"] == tag]:
        print(group_dict["\\ps"], gold_tag)
        group_dict["\\ps"] = gold_tag

out_order = {"\\lx": 0, "\\ps": 1, "\\ge": 2, "\\un": 3, "\\dt": 4}
with codecs.open("/Users/ajwieme/arapaho_library/data/New_Dictionary.txt", "w") as out:
  '''
    If anyone has to read this (I am looking at you, future Adam), I am sorry, Python brings out the worst in me.
    This just returns the group_dicts into a string just like the input,
    and uses out_order to ensure the order of keys is the same.
  '''
  out.write(first_line + '\n\n')
  out.write('\n\n'.join(['\n'.join([k + " " + d[k] for k in sorted(list(d.keys()), key=lambda val: out_order.get(val, 5)) if k]) for d in group_dicts]))