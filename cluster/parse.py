import argparse

from tokenizer import *


def look_for_next_matching_delimiter(tokens):
    stack = []

    for i in range(len(tokens)):
        c = tokens[i][1]

        if c in ["(", "[", "{"]:
            stack.append(c)
        elif c in [")", "]", "}"]:
            if stack[-1] == {")": "(", "]": "[", "}": "{"}[c]:
                stack.pop()
            else:
                raise Exception("Mismatched delimiters")

        if len(stack) == 0:
            return i

    raise Exception("Mismatched delimiters")


grammar_piece = set()


def join_chunks(chunks):
    acc = chunks[0]
    i = 1

    while i < len(chunks):
        next = chunks[i]
        last = acc.pop()
        first = next.pop(0)

        acc.append(("matched", last[1] + first[1]))
        acc.extend(next)

        i += 1

    return acc


def delimit_chunk(chunk):
    seq = []
    acc = []

    for token in chunk:
        if token[0] in ["sequence"]:
            if len(seq) > 0:
                acc.append(" ".join(seq))
                seq = []
            acc.append(token[1])
        elif token[0] in ["matched"]:
            seq.append(token[1])
        else:
            seq.append(token[0])

    for p in acc:
        grammar_piece.add(p)


def parse(tokens):
    start = 0
    i = 0
    chunks = []

    while i < len(tokens):
        if tokens[i][1] in ["(", "[", "{"]:
            j = look_for_next_matching_delimiter(tokens[i:])
            chunks.append(tokens[start : i + 1])
            parse(tokens[i + 1 : i + j])
            start = i + j
            i += j + 1
            continue

        i += 1

    chunks.append(tokens[start:])
    joined = join_chunks(chunks)
    split = delimit_chunk(joined)

    return split


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", type=str, default=None)
    parser.add_argument("files", type=str, nargs="+")

    for p in parser.parse_args().files:
        f = open(p, "r")
        s = f.read()

        print(s)
        tokens = tokenize(s, c_keywords)
        parse(tokens)

    sorted = sorted(list(grammar_piece))
    for p in sorted:
        print(repr(p))

    print(len(sorted))
