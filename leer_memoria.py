from pymem import Pymem
from pymem.process import module_from_name

# Nombre del proceso del juego
PROCESS_NAME = "DBOG.exe"

# Offsets ficticios (debes encontrarlos con Cheat Engine)
OFFSET_HP = 0x0073D878
OFFSET_MP = 0x0073D874

# Leer proceso
pm = Pymem(PROCESS_NAME)
module = module_from_name(pm.process_handle, PROCESS_NAME)
base_addr = module.lpBaseOfDll

def read_hp_mp():
    hp = pm.read_int(base_addr + OFFSET_HP)
    mp = pm.read_int(base_addr + OFFSET_MP)
    return hp, mp

while True:
    hp, mp = read_hp_mp()
    print(f"HP: {hp}, MP: {mp}")