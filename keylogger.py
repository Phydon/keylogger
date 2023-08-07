import os
import sys
from pynput import keyboard


FILEPATH = os.path.join(os.path.dirname(__file__), "keylog.txt")
DICTIONARY_PATH = os.path.join(os.path.dirname(__file__), "dictionary.txt")
EXE_PATH = os.path.join(os.path.dirname(__file__), "target/release/wordlog.exe")
words = []
text = ""


# load dictionary
def load_words(dictionary_path):
    with open(dictionary_path) as word_file:
        words = set(word_file.read().split())

    return words


def remove_special_chars(word):
    special_chars = "?!.;:§-_"
    for char in special_chars:
        word = word.replace(char, '').strip()

    return word
        
    
def valid_word(word):
    return True if word.isalpha() and word.find("Key.") == -1 else False


def word_in_dictionary(dictionary, word):
    return True if word.strip().lower() in dictionary else False
    

def write_to_file(filepath, dictionary, words):
    try: 
        with open(filepath, "a") as writer:
            for word in words:
                word = remove_special_chars(word)
                if valid_word(word) and word_in_dictionary(dictionary, word):
                    writer.write(word.lower())
                    writer.write('\n')

            # FIXME -> needed?
            writer.truncate()
    except Exception as e:
        print(f"Error while writing to file: {e}")
        sys.exit()


def on_press(key):
    # TODO for debugging only -> remove later
    # try:
    #     print(key.char)
    # except AttributeError:
    #     print(key)
        
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
        print("::: Populating file ...")
        write_to_file(FILEPATH, dictionary, words)
        words = []
        
        # Stop listener
        print("::: Quitting")
        return False

def process_file_with_rust(path_to_executable):
    os.system(path_to_executable)


if __name__ == "__main__":
    try: 
        print("::: Loading dictionary ...")
        dictionary = load_words(DICTIONARY_PATH)
        
        print("::: Keylogger is running ...")
        # Collect events until released
        with keyboard.Listener(
                on_press=on_press,
                on_release=on_release) as listener:
            listener.join()

        try: 
            process_file_with_rust(EXE_PATH)
        except Exception as e:
            print(f"Error while executing external executable: {e}")
            sys.exit()
    except KeyboardInterrupt:
        sys.exit()
