from arapaho_library import text

"""
  This is meant to be used to parse the results of a query on the corpus, which has the schema of
  {ID:, name: TextName, lines:
    {ref: ref, free_translation: ft, speaker: speaker, words:
      {word: word, morphemes:
        {morpheme: morpheme, pos: pos, gloss: gloss}
      }
    }
  }
"""
def get_text_examples(options, text_object):
  text_examples = []

  for k, v in options.items():
    if k == "name":
      text_object.name = v
    elif k == "lines":
      for line in v:
        words = line.pop("words")
        text_example = text.TextExample(line)
        text_example.speaker = line.pop("speaker")
        for word in words:
          ws = text_example.add_word_segment(word.get("word"))
          for morpheme in word.get("morphemes"):
            ws.add_morpheme_segment(morpheme)

        text_examples.append(text_example)

  return text_examples