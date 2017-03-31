# -*- coding: utf-8 -*-

from text import *
from lexicon import *
from aligner import Aligner

text = Text()
lexicon = Lexicon()

text.parse("../data/77b.txt")
lexicon.parse("../data/arapaho_lexicon.json")

aligner = Aligner(text, lexicon)

aligner.align("../data/new_test_text_file.txt", "../data/test_log_file.txt")
