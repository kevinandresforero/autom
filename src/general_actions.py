import time
import pyautogui

class GeneralActions:
    """
    General actions for bot control, such as pressing and holding keys,
    and reading HP/MP from memory.
    """

    def __init__(self, pm=None, offset_hp=None, offset_mp=None):
        """
        Args:
            pm: Pymem instance for memory reading (optional).
            offset_hp: Memory offset for HP (optional).
            offset_mp: Memory offset for MP (optional).
        """
        self.pm = pm
        self.offset_hp = offset_hp
        self.offset_mp = offset_mp

    def press_key(self, key):
        """
        Presses a key using pyautogui.

        Args:
            key (str): Key to press.
        """
        if key != 'v':
            time.sleep(0.2)
        pyautogui.press(str(key))

    def hold_key(self, key):
        """
        Holds a key for 0.9 seconds.

        Args:
            key (str): Key to hold.
        """
        pyautogui.keyDown(key)
        time.sleep(0.9)
        pyautogui.keyUp(key)

    def press_combo(self, key1, key2, delay=0.1):
        """
        Presiona dos teclas al mismo tiempo (por ejemplo, para combos como ALT+1).

        Args:
            key1 (str): Primera tecla (por ejemplo, 'alt').
            key2 (str): Segunda tecla (por ejemplo, '1').
            delay (float): Tiempo en segundos entre presionar y soltar las teclas.
        """
        import pyautogui
        pyautogui.keyDown(key1)
        time.sleep(0.05)
        pyautogui.press(key2)
        time.sleep(delay)
        pyautogui.keyUp(key1)