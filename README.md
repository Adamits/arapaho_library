# arapaho_library

Library for interfacing with Arapaho Lexicon and IGT at CU Boulder

Make sure to set paths to the corpus and lexicon in the config.txt file, then, to instantiate a list of lexical entry objects:
```
from arapaholexicalparser import *
lexical_parser = ArapahoLexicalParser()
lexical_parser.parse()
```

The list of lixical entries is now available at lexical_parser.lexical_entries

And to instantiate a list of text entry objects:

```
from arapahotextparser import *
text_parser = ArapahoTextParser()
text_parser.parse()
```

the list of text example objects is now available at text_parser.examples
