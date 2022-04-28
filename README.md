# Japanese Vocabulary Note Generator (JVNG)

Given a list of new line separated vocabulary words in Japanese, JVNG generates Anki notes in 
the bulk input form, while also moving any media to the anki media folder. 

I built this to cut the 2+ hours spent making flashcards for Japanese class to 5 minutes. It was done in a couple hours and probably buggy.

`cardgen.py` is the script to run; you'll need have [requests](https://docs.python-requests.org/en/latest/) installed in whatever python environment you wish to run it with.

If you wish to use it, take a look at the script. I tried to document it as I go. 

JVNG uses data from [KanjiAlive](https://github.com/kanjialive/kanji-data-media) for stroke 
animations and some audio, [JMdict-EDICT Dictionary Project](http://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project)
for word lookup, meanings and example sentences and Google Translate API for some audio.


Note that audio files are not saved in the repo. To obtain audio files from KanjiAlive, download them from one of the 
links found at the bottom of [this guide](https://github.com/kanjialive/kanji-data-media/tree/master/examples-audio).

This project should not be used for any commerical purposes; personal use only.
