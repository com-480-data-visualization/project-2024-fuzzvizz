import os
import re
import glob
import argparse

import numpy as np
import polars as pl

from sklearn import linear_model
from collections import Counter


sequence_delimiters = [r",\s*", r":\s*", r";\s*", r"\n\s*"]

matching_delimiters = ["(", ")", "[", "]", "{", "}"]

other_delimiters = ["@", "@@", "#", "##", "$", "$$", "?", "::", ".", "->", "=>"]

unary_operators = ["~", "!"]

binary_operators = [
    "-",
    "+",
    "*",
    "/",
    "%" "**",
    "&",
    "|",
    "^",
    "<<",
    ">>",
    ">>>",
    "&&",
    "||",
]

assignment_operators = [
    "=",
    ":=",
    "-=",
    "+=",
    "*=",
    "/=",
    "%=" "**=",
    "&=",
    "|=",
    "^=",
    "<<=",
    ">>=",
    ">>>=",
]

comparison_operators = [">", ">=", "<", "<=", "==", "===", "!=", "!==", "<=>"]

other_operators = [
    "..",
    "...",
    "..=",
]

c_keywords = [
    "alignas",
    "alignof",
    "auto",
    "break",
    "case",
    "const",
    "constexpr",
    "continue",
    "default",
    "do",
    "else",
    "enum",
    "extern",
    "for",
    "goto",
    "if",
    "inline",
    "register",
    "restrict",
    "return",
    "sizeof",
    "static",
    "static_assert",
    "struct",
    "switch",
    "thread_local",
    "typedef",
    "typeof",
    "typeof_unqual",
    "union",
    "volatile",
    "while",
]

js_keywords = [
    "abstract",
    "await",
    "break",
    "case",
    "catch",
    "class",
    "const",
    "continue",
    "debugger",
    "default",
    "delete",
    "do",
    "else",
    "enum",
    "eval",
    "export",
    "extends",
    "false",
    "final",
    "finally",
    "for",
    "function",
    "goto",
    "if",
    "implements",
    "import",
    "in",
    "instanceof",
    "interface",
    "let",
    "native",
    "new",
    "package",
    "private",
    "protected",
    "public",
    "return",
    "static",
    "super",
    "switch",
    "synchronized",
    "throw",
    "throws",
    "transient",
    "try",
    "typeof",
    "var",
    "volatile",
    "while",
    "with",
    "yield",
]

identifiers = r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"

numerics = [
    r"0[xX][0-9a-fA-F]+",
    r"0[bB][01]+",
    r"0[oO][0-7]+",
    r"[0-9]+",
    r"[0-9]*\.[0-9]+",
    r"[0-9]+\.[0-9]*",
    r"[0-9]+\.[0-9]*[eE][+-]?[0-9]+",
]

strings = [
    r'"(?:[^"\\]|\\.)*"',
    # r"\"[^\"]*\"",
    # r"'[^']*'",
    # r"`[^`]*`",
]

comments = [
    r"//.*",
    r"#.*",
    r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/",
]


def union(arr, escape=False, word_boundary=False):
    def helper(w):
        if escape:
            w = re.escape(w)
        if word_boundary:
            w = r"\b" + w + r"\b"
        return w

    return "|".join([helper(w) for w in arr])


def tokenize(code, keywords):
    patterns = {
        "comment": union(comments),
        "string": union(strings),
        "keyword": union(keywords, escape=True, word_boundary=True),
        "numeric": union(numerics, word_boundary=True),
        "identifier": identifiers,
        "sequence": union(sequence_delimiters),
        "match": union(matching_delimiters, escape=True),
        "unary": union(unary_operators, escape=True),
        "binary": union(binary_operators, escape=True),
        "assignment": union(assignment_operators, escape=True),
        "comparison": union(comparison_operators, escape=True),
        "other": union(other_delimiters + other_operators, escape=True),
    }

    master_pattern = re.compile(
        "|".join(["(?P<%s>%s)" % (name, pattern) for name, pattern in patterns.items()])
    )

    # Tokenize the code
    tokens = []
    for match in re.finditer(master_pattern, code):
        token_type = match.lastgroup
        token_value = match.group(token_type)
        if token_value[0] in [",", ":", ";", "\n"]:
            token_value = token_value[0]

        if token_type == "comment":
            continue

        tokens.append((token_type, token_value))

    return tokens


def count_tokens(files):
    dicts = []
    for f in files:
        with open(f, "r", errors="ignore") as s:
            # Strip comments
            code = s.read()
            code = re.sub(r"//.*", "", code)
            code = re.sub(r"#.*", "", code)

            tokens = tokenize(code)

            # Count the tokens
            counts = Counter(tokens)
            dicts.append(counts)

    return pl.from_dicts(dicts).fill_null(0)


def tokens_count_fit_lasso():
    files = glob.glob("v8/**/*.js", recursive=True)
    df = count_tokens(files)

    for c in df.columns:
        y = df.get_column(c).to_numpy()
        X = df.with_columns(pl.lit(1).alias(c)).to_numpy()
        X = X + np.random.normal(0, 0.1, X.shape)

        lasso = linear_model.Lasso(alpha=1000)
        lasso.fit(X, y)

        print(f"{c} = ")
        for i, coef in enumerate(lasso.coef_):
            if coef > 0.1:
                print(f" + {coef:.4f} * '{df.columns[i]}'", end="")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", type=str, default=None)
    parser.add_argument("input", type=str)

    args = parser.parse_args()

    if args.language == None:
        ext = os.path.splitext(args.input)[1]
        if ext in [".c", ".js"]:
            args.language = ext

    if args.language == ".c":
        keywords = c_keywords
    elif args.language == ".js":
        keywords = js_keywords
    else:
        keywords = []

    with open(args.input, "r", errors="ignore") as s:
        tokens = tokenize(s.read(), keywords)
        for t in tokens:
            print(t)
        print(" ".join([t[1] for t in tokens]))
