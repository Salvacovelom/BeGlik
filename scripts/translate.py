# pip install googletrans==3.1.0a0
# pip install polib

import time
import polib
from googletrans import Translator

translator = Translator()

def main():
    # target file where we will do auto translation using the msgid field
    filename = "../locale/es/LC_MESSAGES/django.po"
    po = polib.pofile(filename)

    batch_size = 50
    it = 0
    sleep_time = 1 * 60

    while 1:
        batch = po[it : it + batch_size + 1]
        itt = ((len(po) - it) / batch_size).__ceil__()
        tot = (len(po) / batch_size).__ceil__()
        print(tot-itt, "/", tot) # print progress
        if not batch:
            break
        batch_in = [b.msgid for b in batch]
        try:
            # do the translation from es to en
            trans = translator.translate(batch_in, src="en", dest="es")
            for entry, t in zip(batch, trans):
                entry.msgstr = t.text
            it += batch_size
        except Exception as e:
            print("sleeping", sleep_time)
            time.sleep(sleep_time)

    po.save(filename)


main()