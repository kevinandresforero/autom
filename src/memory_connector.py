import time
from pymem import Pymem
from pymem.process import module_from_name

class MemoryConnection:
    """
    Handles connection to the game process and loads the game module base address.

    Example:
        mem_conn = MemoryConnection("Game.exe")
        pm = mem_conn.pm
        base_addr = mem_conn.base_addr
    """

    def __init__(self, process_name):
        """
        Initializes the memory connection and loads the base address.

        Args:
            process_name (str): Name of the process to connect to.
        """
        self.pm = self.wait_for_process(process_name)
        self.base_module = module_from_name(self.pm.process_handle, process_name)
        if self.base_module is None:
            raise Exception("[X] Game module not found.")
        self.base_addr = self.base_module.lpBaseOfDll

    def wait_for_process(self, process_name):
        """
        Waits for the process to start and returns a Pymem instance.

        Args:
            process_name (str): Name of the process to wait for.

        Returns:
            Pymem: Instance connected to the process.
        """
        while True:
            try:
                pm = Pymem(process_name)
                return pm
            except Exception:
                print("[!] Waiting for the game to start...")
                time.sleep(1)