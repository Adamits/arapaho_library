from arapaho_library import text as arapaho_text
#TODO Need to add ElanParticipant parsing, like in txt_parser

def get_text_examples(soup, text_object):
  '''
    expects path to xml file
    This parses similarly to _parse_txt, but it instantiates a BeautifulSoup object
    and builds the text examples from there. XML is preferred, as the structure makes
    alignment less ambiguous
  '''
  text_examples = []
  for ref_group in soup.children:
    try:
      ref = ref_group.ref
    except:
      ref = None
    if ref:
      # ft is sometimes in the refgroup, sometimes after it below ELAN info
      try:
        ft = ref_group.ft.get_text()
      except:
        try:
          ft = ref_group.find_next_sibling("ft").get_text()
        except:
          ft = None

      text_example = arapaho_text.TextExample({"ref": ref.get_text(), "free_translation": ft})
      for i, tx_group in enumerate(ref_group.children):
        try:
          text = tx_group.tx.get_text()
        except:
          text = None

        if text:
          word_segment = text_example.add_word_segment(text)

          morpheme_dict = {}
          for child in tx_group.children:
            # mb should be the first node in a new MorphemeSegment
            if child.name == "mb":
              morpheme_dict["morpheme"] = child.get_text()
            elif child.name == "ge":
              morpheme_dict["gloss"] = child.get_text()
            elif child.name == "ps":
              morpheme_dict["pos"] = child.get_text()

            if set(morpheme_dict.keys()) == set(["morpheme", "gloss", "pos"]):
              word_segment.add_morpheme_segment(morpheme_dict)
              morpheme_dict = {}

      text_examples.append(text_example)

  return text_examples
