# arapaho_library

Library for interfacing with Arapaho Lexicon and IGT at CU Boulder

Mostly `text.py` `lexicon.py` and `nput_parsers/*` are useful.

Run the following to install dependencies:
```
$ pip install -r requirements.txt
```

To instantiate a list of lexical entry objects:
```
from lexicon import *
lexicon = Lexicon()
lexicon.parse("path to lexicon.json")
```

The list of lixical entries is now available at lexical_parser.lexical_entries

And to instantiate a list of text entry objects:

```
from text import *
text = Text()
text.parse("path to corpus.txt")
```

the list of text example objects is now available at text_parser.examples
