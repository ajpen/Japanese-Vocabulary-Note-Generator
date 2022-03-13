import sys
import os
import json


def load_data():
    with open("jmdict.json") as f:
        jmlookup = json.load(f)

    with open("kanalookup.json") as f:
        kanji = json.load(f)

    return jmlookup, kanji

def generate_card(word):



def main():
    if len(sys.argv) < 3:
        exit(f"Usage: ./{sys.argv[0]} vocab_list output_file OPTIONAL:tag1 tag2...")

    jp_lookup, kanji_lookup = load_data()

    new_words_f = open(sys.argv[1])
    output_f = open(sys.argv[2], 'w')


    # Write tags first
    if len(sys.argv) > 3:
        tags = " ".join(sys.argv[3:])
        output_f.write(f"tags:{tags}\n")

    for word in new_words_f:
        word = word.strip()

        card = generate_card(word)
        output_f.write(f"{card}\n")

    output_f.close()
    new_words_f.close()