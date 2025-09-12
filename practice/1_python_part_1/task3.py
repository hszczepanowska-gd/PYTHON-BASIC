"""
Write function which receives list of text lines (which is space separated words) and word number.
It should enumerate unique words from each line and then build string from all words of given number.
Restriction: word_number >= 0
Examples:
    >>> build_from_unique_words('a b c', '1 1 1 2 3', 'cat dog milk', word_number=1)
    'b 2 dog'
    >>> build_from_unique_words('a b c', '', 'cat dog milk', word_number=0)
    'a cat'
    >>> build_from_unique_words('1 2', '1 2 3', word_number=10)
    ''
    >>> build_from_unique_words(word_number=10)
    ''
"""
from typing import Iterable


def build_from_unique_words(*lines: Iterable[str], word_number: int) -> str:
    result = []
    for line in lines:
        unique_set = set()
        unique_words = []
        words = line.split()
        
        for word in words:
            if word not in unique_set:
                unique_set.add(word)
                unique_words.append(word)
    
        if len(unique_words) > word_number:
            result.append(unique_words[word_number])
    
    return ' '.join(result)


def test_build_from_unique_words():
    assert build_from_unique_words('a b c', '1 1 1 2 3', 'cat dog milk', word_number=1) == 'b 2 dog'
    assert build_from_unique_words('a b c', '', 'cat dog milk', word_number=0) == 'a cat'
    assert build_from_unique_words('1 2', '1 2 3', word_number=10) == ''
    assert build_from_unique_words(word_number=10) == ''

test_build_from_unique_words()