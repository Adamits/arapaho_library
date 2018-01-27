# -*- coding: utf-8 -*-
from lexicon import *
from bs4 import BeautifulSoup
from input_parsers import xml_parser, txt_parser, dict_parser
import collections

# Note that x= dict[key], where key points to another dict
# seems to store a pointer to that dict in python, so updating
# an attribute of a LexicalEntry SHOULD also update the json...

class Text(object):
  '''
    A Text object is meant to represent a single "text" in the corpus, which should be the output of
    toolbox and have a unique id. This can be either in XML or .txt format. This can also be a "master" .txt,
    which might append all of the files to one file. In this case there is no unique ID
    a Text has many TextExamples, which are basically a line with a unique translation (ft), and a unique reference id (ref)
    And a TextExample comprises many segments, which are each interlinearized morphemes
  '''
  def __init__(self, name="", options={}):
    self.name = name
    self.text_examples          = []
    self.refs              = []
    self.refs_and_examples = {}
    self.input_type = ""
    self.text_ids = []
    self._parse_options(options)

  def parse(self, text_path):
    '''
      :param text_path: path to the file, which is a toolbox output of either XML (preferred for alignment) or txt
      :return: None, it simply sets the .examples attribute to a list of 'examples', or objects that represent a single line with a unique ref
    '''
    if text_path.endswith(".xml"):
      self.input_type = "xml"
      self._parse_xml(text_path)
    elif text_path.endswith(".txt"):
      self.input_type = "txt"
      self._parse_txt(text_path)

  def _parse_txt(self, text_path):
    # Get all lines from text, removing trailing whitespace
    lines = [line.strip() for line in codecs.open(text_path, encoding="Latin-1")]
    for text_example in txt_parser.get_text_examples(lines, self):
      self.add_text_example(text_example)

  def _parse_xml(self, text_path):
    soup = BeautifulSoup(codecs.open(text_path, encoding="Latin-1"), "lxml")
    for id_group in soup.find_all("idgroup"):
      for text_example in xml_parser.get_text_examples(id_group, self):
        self.add_text_example(text_example)

  def _parse_options(self, options):
    """
    This is meant to be used to parse the results of a query on the corpus
    """
    if options:
      [self.add_text_example(te) for te in dict_parser.get_text_examples(options, self)]

  def add_text_example(self, text_example):
    text_example.parent_text = self
    self.text_examples.append(text_example)
    self.refs.append(text_example.ref)
    self.text_ids.append(text_example.text_id)

  def mb_ps_tuples_and_examples(self):
    mb_ps_dict = {}
    for example in self.text_examples:
      for mb_ps in example.mb_and_ps_tuples():
        mb_ps_dict.setdefault(mb_ps, []).append(example)

    return mb_ps_dict

  def get_morpheme_segments(self):
    """
    returns a list of every get morpheme segment in the text
    """
    return [ms for text_example in self.text_examples for ms in text_example.get_morpheme_segments()]

  def get_pos(self):
    """
    returns a list of every get pos tag in the text
    """
    return [morpheme_segment.pos for morpheme_segment in self.get_morpheme_segments()]

  def refs(self):
    return[text_example.ref for text_example in self.text_examples]

  def examples_as_dicts(self):
    return [example.dict_with_segmentation() for example in self.text_examples]

  def text_example_count(self):
    return len(self.text_examples)

  def write(self, filename):
    with open(filename, 'w') as outfile:
      outfile.write('\n\n'.join([example.write_string() for example in self.text_examples]))

  #def concordance(self, input_lex, input_pos, window=5):

  def json_format(self):
    """
    Returns a list of dicts for each 'text', i.e. one for each unique id in the file.
    This is because a "Text" object corresponds to a single file, but one file, as it turns out
    may or may not comprise multiple individual texts in the corpora.

    This method will call every sub'level's json_format() method, in turn, so we get a large dictionary
    that corresponds t the schema of the mongo database.
    """
    text_id_and_example = {}
    for text_example in self.text_examples:
      text_id_and_example.setdefault(text_example.text_id, [])
      text_id_and_example[text_example.text_id].append(text_example.json_format())

    return [{"name": t_id, "lines": exs} for t_id, exs in text_id_and_example.items()]

class TextExample(object):

  def __init__(self, options={}):
    self.ref = options.get("ref", "")
    self.free_translation = options.get("free_translation", "")
    self.word_segments = []
    self.parent_text = options.get("parent_text")
    self.text_id = self._get_text_id()
    self.speaker = ""

  def _get_text_id(self):
    return self.ref.split('.')[0]

  def string(self):
    return ' '.join([w.string for w in self.word_segments])

  def contains_data(self):
    return self.word_segments or self.free_translation

  def contains_ref(self):
    return self.ref != ""

  def add_word_segment(self, string):
    '''
       Instantiates a word_segment and adds it to self.word_segments
       with index that assumes the string being added is the next word
       in the text_example
    '''
    index = len(self.word_segments)
    word_segment = WordSegment({"string": string, "index": index, "text_example": self})
    self.word_segments.append(word_segment)

    return word_segment

  def get_morpheme_segments(self):
    """
    returns a list of every morpheme segment in the text example
    """
    return [ms for word_segment in self.word_segments for ms in word_segment.get_morpheme_segments()]

  def get_pos(self):
    """
    returns a list of every get pos tag in the text example
    """
    return [morpheme_segment.pos for morpheme_segment in self.get_morpheme_segments()]

  def get_mb_list(self):
    return [m.morpheme for m in self.get_morpheme_segments()]

  def get_ge_list(self):
    return [m.gloss for m in self.get_morpheme_segments()]

  def write_toolbox_txt_format(self):
    return '\n'.join(["\%s %s" % (label, val) for label, val in self.igt_tuples()])

  def json_format(self):
    formatted_dict = {"ref": self.ref, "free_translation": self.free_translation, "speaker": self.speaker, "words": []}
    for ws in self.word_segments:
      formatted_dict["words"].append(ws.json_format())

    return formatted_dict


class WordSegment(object):

  def __init__(self, options ={}):
    self.string = options.get("string", "")
    self.text_example = options.get("text_example")
    self.index = options.get("index")
    self.morpheme_segments = []

  def add_morpheme_segment(self, options):
    '''
       Instantiates a morpheme_segment and adds it to self.morpheme_segments
       with index that assumes the string being added is the next morpheme
       in the word_segment
    '''
    index = len(self.morpheme_segments)
    options.update({"index": index, "word_segment": self})
    morpheme_segment = MorphemeSegment(options)
    self.morpheme_segments.append(morpheme_segment)

    return morpheme_segment

  def previous(self):
    try:
      return self.text_example.word_segments[self.index - 1]
    except:
      return "<s>"

  def next(self):
    try:
      return self.text_example.word_segments[self.index + 1]
    except:
      return "</s>"

  def json_format(self):
    formatted_dict = {"word": self.string, "morphemes": []}
    for ms in self.morpheme_segments:
      formatted_dict["morphemes"].append(ms.json_format())

    return formatted_dict

  def get_morpheme_segments(self):
    """
    returns a list of every morpheme_segment in the word segment
    """
    return self.morpheme_segments

  def get_pos(self):
    """
    returns a list of every pos tag in the word segment
    """
    return [morpheme_segment.get_pos for morpheme_segment in self.morpheme_segments]


class MorphemeSegment(object):

  def __init__(self, options={}):
    self.morpheme = options.get("morpheme", "")
    self.gloss = options.get("gloss", "")
    self.pos = options.get("pos", "")
    self.word_segment = options.get("word_segment")
    self.index = options.get("index")

  def __str__(self):
    return str(self.morpheme, self.gloss, self.pos)

  def previous(self):
    try:
      return self.word_segment.morpheme_segments[self.index - 1]
    except:
      return "<m>"

  def next(self):
    try:
      return self.word_segment.morpheme_segments[self.index + 1]
    except:
      return "</m>"

  def json_format(self):
    return {"morpheme": self.morpheme, "pos": self.pos, "gloss": self.gloss}


def run_test():
  x = Text()
  x.parse()
