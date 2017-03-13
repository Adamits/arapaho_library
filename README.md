# arapaho_library

Library for interfacing with Arapaho Lexicon and IGT at CU Boulder

To instantiate a list of lexical entry objects:
```
from arapaholexicalparser import *
lexical_parser = ArapahoLexicalParser()
lexical_parser.parse("path to lexicon.json")
```

The list of lixical entries is now available at lexical_parser.lexical_entries

And to instantiate a list of text entry objects:

```
from arapahotextparser import *
text_parser = ArapahoTextParser()
text_parser.parse("path to corpus.txt")
```

the list of text example objects is now available at text_parser.examples
