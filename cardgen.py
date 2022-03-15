import sys
import shutil
import os
import os.path
import json
import requests
import csv
import time
import traceback
import uuid


ANIMATION_PATH = "/Users/anfernee/projects/anki-japanese-note-generator/animations"
AUDIO_PATH = "/Users/anfernee/projects/anki-japanese-note-generator/audio-mp3"
ANKI_MEDIA_FOLDER = "/Users/anfernee/Library/Application Support/Anki2/User 1/collection.media"
DOWNLOAD_TEMP_FOLDER = "/tmp"


if len(sys.argv) < 3:
    sys.exit(f"Usage: ./{sys.argv[0]} vocab_list output_file OPTIONAL:tag1 tag2...")


""" #################### Load Lookup Data ###########################"""
"""
jmdict fields are:
kana: the reading in hiragana
kanji: the kanji for the word
meanings: list of meanings for the word
example: either empty string or a tuple in the form (japanese, english)
"""
with open("jmdict.json") as f:
    jmlookup = json.load(f)


"""
kanjilookup maps a kanji to the romanji key used by KanjiAlive data
fields are:
romanji: used for lookup with kanjilive media
meaning: meaning of a single kanji
examples: examples of words containing the kanji
"""
kanjilookup = dict()

with open("ka_data.csv") as f:
    reader = csv.reader(f)

    # skip header
    next(reader)

    for row in reader:
        kanjilookup[row[0]] = {
            'romanji': row[1],
            'meaning': row[3],
            'examples': [x[0].split()[0] for x in json.loads(row[9])]
        }


"""
#################################### METHODS ##################################### """


def download_audio(word):
    """
    Tries to download audio using google translate api
    :param word: the word whose audio we seek
    :return: path to downloaded file. Throws exception on error
    """

    word_file = f"{uuid.uuid4().hex}.mp3"
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&total=1&idx=0&textlen=32&client=tw-ob&q={word}&tl=ja"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/39.0.2171.95 Safari/537.36'}

    # First, we'll download the file to cwd then we'll try to copy to the anki media folder.
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ValueError(f"Attempt to download audio for {word} failed.")

    src = os.path.join(DOWNLOAD_TEMP_FOLDER, word_file)

    with open(src, 'wb') as f:
        f.write(response.content)

    # move audio to anki path
    dest = os.path.join(ANKI_MEDIA_FOLDER, word_file)

    shutil.copyfile(src, dest)
    return word_file


def kanji_alive_audio_lookup(word):
    """
    given 'word', check if the word exists in the example, and if it does, move it to the anki media folder
    :param word: the full word using kanji
    :return: the name of the audio file if successful; or None if not found. Exceptions raised on error
    """

    index = None
    romanji = None

    # we need to look up all the kanji in the word, then check its existence in kanji alive
    kanji_examples = [kanjilookup[x] for x in word if kanjilookup.get(x)]

    for examples in kanji_examples:
        for j, examp in enumerate(examples['examples']):
            kanji = examp.split("（")[0].strip()
            if kanji == word:
                index = j + 97  # examples are indexed by lowercase letters in alpha order
                romanji = examples["romanji"]
                break
        else:
            continue
        break

    if not (index and romanji):
        return None

    audio_name = f"{romanji}_06_{chr(index)}.mp3"
    src = os.path.join(AUDIO_PATH, audio_name)
    dst = os.path.join(ANKI_MEDIA_FOLDER, audio_name)

    shutil.copyfile(src, dst)
    return audio_name


def import_audio(word):
    """
    Given a jp word, copies/downloads the audio for the word in the anki media folder
    First check if the word is in Kanji alive dataset. If not, get it from translate api
    :param word: word whose audio is downloaded/copied
    :return: the audio file name; raises an exception on error
    """

    word_file = kanji_alive_audio_lookup(word)

    if not word_file:
        word_file = download_audio(word)
        time.sleep(120)  # Lets wait a bit so we dont get IP banned

    return word_file


def import_stroke_order_animation(kanji):
    """
    Given a kanji, copies the animation file to the anki media folder.
    :param kanji: single kanji whose stroke order animation is needed
    :return: the animation file name; raises an exception on error
    """
    romanji = kanjilookup.get(kanji, None)

    if not romanji:
        return None

    anim_fname = f"{romanji['romanji']}_00.mp4"
    anim_path = os.path.join(ANIMATION_PATH, anim_fname)
    dest_path = os.path.join(ANKI_MEDIA_FOLDER, anim_fname)

    shutil.copyfile(anim_path, dest_path)

    return anim_fname


def generate_card(word):
    """
    Card is a line of fields separated by semi colons.
    We'll get the fields from our lookup functions/dicts
    The fields are:
    kanji; furigana; meaning; audio; example; Kanji Meanings; stroke1; stroke2; stroke3; stroke4

    audio and stroke_ fields are media file names. either this script
    will be responsible for importing them during card generation.

    :param word: The word for which we're generating a card
    :return: string of fields separated by semi colons.
    """
    word_data = jmlookup.get(word)
    if not word_data:
        print(f"{word} isn't in the dictionary. Maybe its not in dict form?")

    else:
        # If theres no kanji, put kana in kanji's place
        word_data["kanji"] = word_data["kanji"] or word_data["kana"]

        word_data["strokes"] = [import_stroke_order_animation(kanji) for kanji in word]
        word_data["strokes"] = [f"[sound:{x}]" for x in word_data["strokes"] if x is not None]

        # fill in the blanks if there aren't 4 stroke orders
        missing = 4 - len(word_data["strokes"])

        for _ in range(missing):
            word_data["strokes"].append("")

        word_data["audio"] = import_audio(word)

        word_data["kanji_meaning"] = [f"{x}: {kanjilookup[x]['meaning']}" for x in word if kanjilookup.get(x)]

        if word_data["example"]:
            example = f"\"{word_data['example'][0]}\n{word_data['example'][1]}\""
        else:
            example = ""

        # all's well, so lets create the card
        return f"{word_data['kanji']}; " \
               f"{word_data['kana']}; " \
               f"{', '.join(word_data['meanings'])}; " \
               f"[sound:{word_data['audio']}]; " \
               f"{example}; " \
               f"{', '.join(word_data['kanji_meaning'])}; " \
               f"{'; '.join(word_data['strokes'])} "


def main():

    new_words_f = open(sys.argv[1])
    output_f = open(sys.argv[2], 'w')
    missing = open(f"{sys.argv[1]}.missing.txt", 'w')

    # Write tags first
    if len(sys.argv) > 3:
        tags = " ".join(sys.argv[3:])
        output_f.write(f"tags:{tags}\n")

    for word in new_words_f:
        word = word.strip()

        try:
            card = generate_card(word)
        except Exception as e:
            print(traceback.format_exc())
            missing.write(f"{word}\n")
            continue

        if card:
            output_f.write(f"{card}\n")
        else:
            missing.write(f"{word}\n")

    output_f.close()
    new_words_f.close()


if __name__ == "__main__":
    main()
