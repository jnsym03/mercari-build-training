def wordPattern(pattern, s):
    words = s.split(' ')
    if len(pattern) != len(words):
        return False

    pattern_to_word = {}
    word_to_pattern = {}
    for p, w in zip(pattern, words):
        if p not in pattern_to_word:
            if w in word_to_pattern:
                return False
            pattern_to_word[p] = w
            word_to_pattern[w] = p
        elif pattern_to_word[p] != w:
            return False

    return True

print(wordPattern("abba", "dog cat cat dog"))  # True
print(wordPattern("abba", "dog cat cat fish"))  # False
print(wordPattern("aaaa", "dog cat cat dog"))  # False
