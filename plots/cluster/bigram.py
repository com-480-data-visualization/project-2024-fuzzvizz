from collections import defaultdict

with open("text.c", "r", errors="ignore") as f:
    text = f.read()

import nltk
import re


def tokenize_c_code(code):
    # Define the token patterns
    patterns = {
        "keyword": r"\b(auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|int|long|register|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while)\b",
        "identifier": r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
        "operator": r"[\+\-\*/%&|\^~!<>=]",
        "numeric": r"\b\d+(\.\d*)?|\.\d+\b",
        "string": r"\".*?\"",
        "comment": r"\/\/.*?$|\/\*.*?\*\/",
    }

    # Create a master pattern
    master_pattern = re.compile(
        "|".join(["(?P<%s>%s)" % (name, pattern) for name, pattern in patterns.items()])
    )

    # Tokenize the code
    tokens = []
    for match in re.finditer(master_pattern, code):
        token_type = match.lastgroup
        token_value = match.group(token_type)
        tokens.append((token_type, token_value))

    return tokens


# tokens = tokenize_c_code(text)
# for token in tokens:
#     print(token)

# tokens = [t for t in tokens if t[0] not in ["identifier", "comment", "numeric", "string"]]


tokens = nltk.wordpunct_tokenize(text)


def train(tokens):
    bigrams = defaultdict(lambda: [])
    for i in range(len(tokens) - 1):
        curr = tokens[i]
        next = tokens[i + 1]

        bigrams[curr].append(next)

    return bigrams


import random


def generate(bigrams):
    curr = random.choice(list(bigrams.keys()))
    for i in range(100):
        print(curr, end=" ")
        next = random.choice(bigrams[curr])
        curr = next


def unique(tokens):
    return list(set(tokens))


print(unique(tokens))

bigrams = train(tokens)
generate(bigrams)
#
