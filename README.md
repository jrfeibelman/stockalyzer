# Stockalyzer
### Author: Jason Feibelman (@jrfeibelman)

CodeBylaws

- Use numpy for representing ints, unsigned ints, & floats
- Avoid for loops where possible, instead use list comprehension
- Use generators where possible to reduce memory overhead
- No global variables
- Use snake_case naming convention for everything besides class names, which should be camelCase
- Use built in functions https://docs.python.org/3/library/functions.html
- Use join for concatenating strings
- Use __slots__ to reduce memory allocation overhead in classes that will be instantiated many times
- Use itertools library for performance
- Use chunking for reading data pd.read_csv("sample.csv", chunksize=chunksize, iterator=True):
- use multiple assignment (ie x,y = 1,2)
- Use direct imports (from math import sqrt) to avoid dot lookups (match.sqrt())
- Use while 1 for infinite while loops instead of True
- Avoid deeply nested if statements
- pypy
- Minimize usage of member variables needed
- Never try to change the internal state of any singleton object
- Use snake_case NOT camelCase


# Usage
Run python -m stockalyzer.main


Old stuff:

## Python Portions

1. 
- [x] Yahoo Finance Data Fetcher
- [ ] Data Storage
    * Hourly & Daily Data Storage
    * Weekly Storage or dynamically calculate on the fly?????

2. Backtesting Performance & Optimizing Parameters
- [x] Backtester (Backtrader) 
    * Performance Matrix
- [x] Machine Learning to optimize parameters

## Needed Functionality

- [ ] Integration between Backtester & Deployment Infrastructure to reuse Strategies
    * Involves integrating C++ code base with Backtrader

## Future Direction

* Add risk management checks before generating a buy/sell signal


# Python Notes
    - If statements with boolean variables: never use is or ==, instead do "if variable"
        - Using 'is' is 60% slower than "if variable", but using '==' is 120% slower!
        - For negation, do 'if not variable'. Using 'is not' is 50% slower and != takes twice as long
        - Using 'is' checks identity while '==' checks values