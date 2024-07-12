import asyncio
import collections
import os.path
import shutil
import subprocess
import time
import traceback
import zipfile
from enum import Flag
from queue import SimpleQueue
from typing import Callable, Optional, Any, Dict, Tuple

from .inc.packages import dolphin_memory_engine

import Utils
from CommonClient import CommonContext, server_loop, gui_enabled, ClientCommandProcessor, logger, \
    get_base_parser
from .Rom import GDLDeltaPatch


class CheckTypes(Flag):
    Runestones = 1
    Bosses = 2
    Legendary_Weapons = 4
    Treasure_Room = 8
    Region_Key = 16



CONNECTION_REFUSED_GAME_STATUS = "Dolphin Connection refused due to invalid Game. Please load the US Version of GDL."
CONNECTION_REFUSED_SAVE_STATUS = "Dolphin Connection refused due to invalid Save. " \
                                 "Please make sure you loaded a save file used on this slot and seed."
CONNECTION_LOST_STATUS = "Dolphin Connection was lost. Please restart your emulator and make sure GDL is running."
CONNECTION_CONNECTED_STATUS = "Dolphin Connected"
CONNECTION_INITIAL_STATUS = "Dolphin Connection has not been initiated"

SCENE_OBJ_LIST_PTR_ADDR = 0x803cb9ec
SCENE_OBJ_LIST_SIZE_ADDR = 0x803cac08

CUR_SCENE_PTR_ADDR = 0x803c2518

GLOBALS_ADDR = 0x803c0558

HEALTH_ADDR = GLOBALS_ADDR + 0x16B0
MAX_HEALTH_ADDR = GLOBALS_ADDR + 0x1738
SHINY_COUNT_ADDR = GLOBALS_ADDR + 0x1B00
SPAT_COUNT_ADDR = GLOBALS_ADDR + 0x1B04
SOCK_PER_LEVEL_COUNT_ADDR = GLOBALS_ADDR + 0x1B08
# MAX_SOCK_PER_LEVEL_ADDR = GLOBALS_ADDR + 0x1B44
# SOCK_CURRENT_LEVEL_ADDR = GLOBALS_ADDR + 0x1B80
LEVEL_PICKUP_PER_LEVEL_ADDR = GLOBALS_ADDR + 0x1b84
# LEVEL_PICKUP_CURRENT_LEVEL_ADDR = GLOBALS_ADDR + 0x1bc0
SOCK_COUNT_ADDR = GLOBALS_ADDR + 0x1BC4
POWERUPS_ADDR = 0x803c0f15
PLAYER_ADDR = 0x803C0C38
PLAYER_CONTROL_OWNER = 0x803c1ce0

# AP free space usage
# notes on free space
# 0x817FFFF6 - 0x817FFFFF
# around 0x8179f890-0x817fcf00 (?)

# @0x817f0080 save game write injection code
# @0x817f0400 save game read injection code


SLOT_NAME_ADDR = 0x8028F2a0
SEED_ADDR = SLOT_NAME_ADDR + 0x40
# we currently write/read 0x20 bytes starting from 0x817f0000 to/from save game
# we could extend up to 0x80 bytes or more if we move AP code from 0x817f0080 to somewhere else
# expected received item index
EXPECTED_INDEX_ADDR = 0x817f0000
# delayed item
BALLOON_KID_COUNT_ADDR = 0x817f0004
SANDMAN_COUNT_ADDR = 0x817f0005
POWER_CRYSTAL_COUNT_ADDR = 0x817f0006
CANNON_BUTTON_COUNT_ADDR = 0x817f0007
SAVED_SLOT_NAME_ADDR = 0x817f0020
SAVED_SEED_ADDR = SAVED_SLOT_NAME_ADDR + 0x40
# some custom code at 0x817f0080



base_id = 5240216

RUNES_PICKUP_IDS = {
    (base_id + 0): (None, ),  # poison field runestone
    (base_id + 1): (None, ),  # mausoleum runestone
    (base_id + 8): (None, ),  # peaks runestone
    (base_id + 16): (None, ),  # armory runestone
    (base_id + 24): (None, ),  # cloud docks runestone
    (base_id + 25): (None, ),  # mothership
    (base_id + 32): (None, ),  # twisted roots
    (base_id + 33): (None, ),  # city ruins
    (base_id + 41): (None, ),  # frozen camp
    (base_id + 42): (None, ),  # crystal mine
    (base_id + 49): (None, ),  # nightmare
    (base_id + 50): (None, ),  # maze
    (base_id + 57): (None, ),  # fortress
}

# (spat name, scene id, id)
BOSS_PICKUP_IDS = {
    (base_id + 100+0): (None, ),
    (base_id + 100+1): (None, ),
    (base_id + 100+2): (None, ),
    (base_id + 100+3): (None, ),
    (base_id + 100+4): (None, ),
    (base_id + 100+5): (None, ),
    (base_id + 100+6): (None, ),
    (base_id + 100+7): (None, ),
    (base_id + 100+8): (None, ),
    (base_id + 100+9): (None, ),
}
LW_PICKUP_IDS = {
    (base_id + 183 + 0): (None, ),
    (base_id + 183 + 1): (None, ),
    (base_id + 183 + 2): (None, ),
    (base_id + 183 + 3): (None, ),
    (base_id + 183 + 4): (None, ),
    (base_id + 183 + 5): (None, ),
    (base_id + 183 + 6): (None, ),
    (base_id + 183 + 7): (None, ),
    (base_id + 183 + 8): (None, ),
}

TREASURE_ROOMS_PICKUP_IDS = {
    (base_id + 210 + 1): (None, ),  # Medusa
    (base_id + 210 + 2): (None, ),  # Minotaur
    (base_id + 210 + 3): (None, ),  # Falconess
    (base_id + 210 + 4): (None, ),  # Unicorn
    (base_id + 210 + 5): (None, ),  # tirgress
    (base_id + 210 + 6): (None, ),  # jackal
    (base_id + 210 + 7): (None, ),  # ogre
    (base_id + 210 + 8): (None, ),  # hyena
    (base_id + 210 + 9): (None, ),  # sumner
    

}
REGION_KEY_PICKUP_IDS = {
    (base_id + 216 + 1): (None, ),  # All FP crystals
    (base_id + 216 + 2): (None, ),  # All MK crystals
    (base_id + 216 + 3): (None, ),  # All CS crystals
    (base_id + 216 + 4): (None, ),  # All SD crystals
    (base_id + 216 + 5): (None, ),  # All FR crystals
    (base_id + 216 + 6): (None, ),  # All DL crystals
    (base_id + 216 + 7): (None, ),  # All ID crystals
    (base_id + 216 + 8): (None, ),  # All DW crystals

    

}
RUNESTONE_ITEM_IDS = {
    (base_id + 0): (None, ), 
    (base_id + 1): (None, ),
    (base_id + 2): (None, ), 
    (base_id + 3): (None, ),  
    (base_id + 4): (None, ), 
    (base_id + 5): (None, ), 
    (base_id + 6): (None, ), 
    (base_id + 7): (None, ), 
    (base_id + 8): (None, ), 
    (base_id + 9): (None, ), 
    (base_id + 10): (None, ), 
    (base_id + 11): (None, ), 
    (base_id + 12): (None, ), 
    

}
SHARD_ITEM_IDS = {
    (base_id + 13): (None, ), 
    (base_id + 14): (None, ), 
    (base_id + 15): (None, ), 
    (base_id + 16): (None, ), 
    (base_id + 17): (None, ), 
    (base_id + 18): (None, ), 
    (base_id + 19): (None, ),
    (base_id + 20): (None, ),
}
LEGENDARY_WEAPON_ITEM_IDS = {
    (base_id + 25): (None, ), #good book
    (base_id + 21): (None, ), #Ice axe
    (base_id + 22): (None, ), #scimitar
    (base_id + 23): (None, ), #javelin
    (base_id + 24): (None, ), #bellows
    (base_id + 26): (None, ), #Lamp
    (base_id + 27): (None, ), #parchment
    (base_id + 28): (None, ), #Lantern
    (base_id + 29): (None, ), #soul savior
    
}
REGION_KEY_ITEM_IDS = {
    (base_id + 30): (None, ), #MK Region key
    (base_id + 31): (None, ), 
    (base_id + 32): (None, ),
    (base_id + 33): (None, ), 
    (base_id + 34): (None, ), 
    (base_id + 35): (None, ), 
    (base_id + 36): (None, ), 
    (base_id + 37): (None, ), #BF Region Key

    
}
WING_KEY_ITEM_IDS = {
    (base_id + 38): (None, ),  #West Wing key
    (base_id + 39): (None, ),  #East Wing Key
    (base_id + 40): (None, ),  #Lower Tower Key
}
#do these need removed?
valid_scenes = [
    b'HB01', b'HB02', b'HB03', b'HB04', b'HB05', b'HB06', b'HB07', b'HB08', b'HB09', b'HB10',
    b'JF01', b'JF02', b'JF03', b'JF04',
    b'BB01', b'BB02', b'BB03', b'BB04',
    b'GL01', b'GL02', b'GL03',
    b'B101',
    b'RB01', b'RB02', b'RB03',
    b'BC01', b'BC02', b'BC03', b'BC04', b'BC05',
    b'SM01', b'SM02', b'SM03', b'SM04',
    b'B201',
    b'KF01', b'KF02', b'KF04', b'KF05',
    b'GY01', b'GY02', b'GY03', b'GY04',
    b'DB01', b'DB02', b'DB03', b'DB04', b'DB05', b'DB06',
    b'B302', b'B303',
]



class GDLCommandProcessor(ClientCommandProcessor):
    def __init__(self, ctx: CommonContext):
        super().__init__(ctx)

    def _cmd_dolphin(self):
        """Check Dolphin Connection State"""
        if isinstance(self.ctx, GDLContext):
            logger.info(f"Dolphin Status: {self.ctx.dolphin_status}")


class GDLContext(CommonContext):
    command_processor = GDLCommandProcessor
    game = 'Gauntlet Dark Legacy'
    items_handling = 0b111  # full remote

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.included_check_types: CheckTypes = CheckTypes.SPAT
        self.items_received_2 = []
        self.dolphin_sync_task = None
        self.dolphin_status = CONNECTION_INITIAL_STATUS
        self.awaiting_rom = False
        self.given_socks = 0
        self.spat_count = 0
        self.sock_count = 0
        self.LAST_STATE = [bytes([0, 0]), bytes([0, 0]), bytes([0, 0])]
        self.last_rev_index = -1
        self.has_send_death = False
        self.last_death_link_send = time.time()
        self.current_scene_key = None

    async def disconnect(self, allow_autoreconnect: bool = False):
        self.auth = None
        await super().disconnect(allow_autoreconnect)

    def on_package(self, cmd: str, args: dict):
        if cmd == 'Connected':
            self.current_scene_key = f"gdl_current_scene_T{self.team}_P{self.slot}"
            self.set_notify(self.current_scene_key)
            self.last_rev_index = -1
            self.items_received_2 = []
            self.included_check_types = CheckTypes.Runestones
            if 'death_link' in args['slot_data']:
                Utils.async_start(self.update_death_link(bool(args['slot_data']['death_link'])))

            self.included_check_types = CheckTypes.Bosses
            self.included_check_types = CheckTypes.Legendary_Weapons
            
            self.included_check_types = CheckTypes.Treasure_Room
        if cmd == 'ReceivedItems':
            if args["index"] >= self.last_rev_index:
                self.last_rev_index = args["index"]
                for item in args['items']:
                    self.items_received_2.append((item, self.last_rev_index))
                    self.last_rev_index += 1
            self.items_received_2.sort(key=lambda v: v[1])
            self._update_item_counts(args)

    def on_deathlink(self, data: Dict[str, Any]) -> None:
        super().on_deathlink(data)
        _give_death(self)

    def _update_item_counts(self, args: dict):
        self.spat_count = len([item for item in self.items_received if item.item == base_id + 0])
        self.sock_count = len([item for item in self.items_received if item.item == base_id + 1])

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            logger.info('Enter the password required to join this game:')
            self.password = await self.console_input()
            return self.password
        if not self.auth:
            if self.awaiting_rom:
                return
            self.awaiting_rom = True
            logger.info('Awaiting connection to Dolphin to get player information')
            return
        await self.send_connect()

    def run_gui(self):
        from kvui import GameManager

        class GDLManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Gauntlet Dark Legacy Client"

        self.ui = GDLManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


def _is_ptr_valid(ptr):
    return 0x80000000 <= ptr < 0x817fffff


def _find_obj_in_obj_table(id: int, ptr: Optional[int] = None, size: Optional[int] = None):
    if size is None:
        size = dolphin_memory_engine.read_word(SCENE_OBJ_LIST_SIZE_ADDR)
    if ptr is None:
        ptr = dolphin_memory_engine.read_word(SCENE_OBJ_LIST_PTR_ADDR)
        if not _is_ptr_valid(ptr): return None
    try:
        counter_list_entry = 0
        # this is our initial index "guess"
        idx = id & (size - 1)
        skip = False
        for i in range(0, size):
            # addr for entry in the list at idx
            counter_list_entry = ptr + idx * 0x8
            if not _is_ptr_valid(counter_list_entry):
                return None
            # get id from the entry
            obj_id = dolphin_memory_engine.read_word(counter_list_entry)
            # if the id matches, we are at the right entry
            if obj_id == id:
                break
            # the returns NULL if it encounters id 0, so just skip if we do
            if obj_id == 0:
                break
            # we are not at the right entry so look at the next
            idx += 1
            # rollover at end of list
            if idx == size:
                idx = 0
        if skip: return -1
        # read counter pointer from the entry
        obj_ptr = dolphin_memory_engine.read_word(counter_list_entry + 0x4)
        if not _is_ptr_valid(obj_ptr):
            return None
        return obj_ptr
    except:
        return None


def _give_spat(ctx: GDLContext):
    cur_spat_count = dolphin_memory_engine.read_word(SPAT_COUNT_ADDR)
    dolphin_memory_engine.write_word(SPAT_COUNT_ADDR, cur_spat_count + 1)
    if cur_spat_count > ctx.spat_count:
        logger.info("!Some went wrong with the spat count!")


def _give_sock(ctx: GDLContext):
    cur_sock_count = dolphin_memory_engine.read_word(SOCK_COUNT_ADDR)
    dolphin_memory_engine.write_word(SOCK_COUNT_ADDR, cur_sock_count + 1)
    if cur_sock_count > ctx.sock_count:
        logger.info("!Some went wrong with the sock count!")


def _give_golden_underwear(ctx: GDLContext):
    cur_max_health = dolphin_memory_engine.read_word(MAX_HEALTH_ADDR)
    dolphin_memory_engine.write_word(MAX_HEALTH_ADDR, cur_max_health + 1)
    dolphin_memory_engine.write_word(HEALTH_ADDR, cur_max_health + 1)
    if cur_max_health > 6:
        logger.info("!Some went wrong with max health!")


def _give_powerup(ctx: GDLContext, offset: int):
    dolphin_memory_engine.write_byte(POWERUPS_ADDR + offset, 1)


def _give_death(ctx: GDLContext):
    if ctx.slot and dolphin_memory_engine.is_hooked() and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS \
            and check_ingame(ctx) and check_control_owner(ctx, lambda owner: owner == 0):
        dolphin_memory_engine.write_word(HEALTH_ADDR, 0)


def _give_level_pickup(ctx: GDLContext, lvl_idx: int):
    assert -1 < lvl_idx < 15, "invalid level index in _give_level_pickup"
    addr = LEVEL_PICKUP_PER_LEVEL_ADDR + 0x4 * lvl_idx
    cur_count = dolphin_memory_engine.read_word(addr)
    dolphin_memory_engine.write_word(addr, cur_count + 1)
    # ToDo: check if we need to write to CurrentLevel too


def _give_shiny_objects(ctx: GDLContext, amount: int) -> object:
    cur_count = dolphin_memory_engine.read_word(SHINY_COUNT_ADDR)
    dolphin_memory_engine.write_word(SHINY_COUNT_ADDR, min(0x01869F, cur_count + amount))


def _inc_delayed_item_count(ctx: GDLContext, addr: int, val: int = 1):
    cur_count = dolphin_memory_engine.read_byte(addr)
    dolphin_memory_engine.write_byte(addr, cur_count + val)


def _get_ptr_from_info(ctx: GDLContext, info: Tuple[bytes, int]):
    if not _check_cur_scene(ctx, info[0]):
        return None
    obj_ptr = _find_obj_in_obj_table(info[1])
    if obj_ptr is None or obj_ptr == -1:
        return None
    return obj_ptr


def _set_counter_value(ctx: GDLContext, cntr_info: Tuple[bytes, int], val: int):
    obj_ptr = _get_ptr_from_info(ctx, cntr_info)
    if obj_ptr is None:
        return
    count_addr = obj_ptr + 0x14
    cur_count = int.from_bytes(dolphin_memory_engine.read_bytes(count_addr, 0x2), "big")
    if cur_count != val:
        dolphin_memory_engine.write_bytes(count_addr, val.to_bytes(0x2, "big"))


def _set_pickup_active(ctx: GDLContext, pickup_info: Tuple[bytes, int]):
    obj_ptr = _get_ptr_from_info(ctx, pickup_info)
    if obj_ptr is None:
        return
    state = dolphin_memory_engine.read_word(obj_ptr + 0x16c)
    if state & 0x8 == 0:  # not collected yet
        current_pickup_flags = int.from_bytes(dolphin_memory_engine.read_bytes(obj_ptr + 0x264, 0x2), "big")
        current_pickup_flags |= 0x2
        dolphin_memory_engine.write_bytes(obj_ptr + 0x264, current_pickup_flags.to_bytes(0x2, "big"))
        current_ent_flags = dolphin_memory_engine.read_byte(obj_ptr + 0x18)
        current_ent_flags |= 0x1
        dolphin_memory_engine.write_byte(obj_ptr + 0x18, current_ent_flags)


def _set_plat_active(ctx: GDLContext, plat_info: Tuple[bytes, int]):
    obj_ptr = _get_ptr_from_info(ctx, plat_info)
    if obj_ptr is None:
        return
    state = dolphin_memory_engine.read_byte(obj_ptr + 0x18)
    if state & 0x1 == 0:
        dolphin_memory_engine.write_byte(obj_ptr + 0x18, state | 0x1)  # visible
    coll_mask = dolphin_memory_engine.read_byte(obj_ptr + 0x22)
    if coll_mask != 0x18:
        dolphin_memory_engine.write_byte(obj_ptr + 0x22, 0x18)  # collision on


def _set_plat_inactive(ctx: GDLContext, plat_info: Tuple[bytes, int]):
    obj_ptr = _get_ptr_from_info(ctx, plat_info)
    if obj_ptr is None:
        return
    state = dolphin_memory_engine.read_byte(obj_ptr + 0x18)
    if state & 0x1 == 0x1:
        dolphin_memory_engine.write_byte(obj_ptr + 0x18, state & ~0x1)  # invisible
    coll_mask = dolphin_memory_engine.read_byte(obj_ptr + 0x22)
    if coll_mask == 0x18:
        dolphin_memory_engine.write_byte(obj_ptr + 0x22, 0)  # collision off


def _set_taskbox_success(ctx: GDLContext, task_info: Tuple[bytes, int]):
    obj_ptr = _get_ptr_from_info(ctx, task_info)
    if obj_ptr is None:
        return
    state_addr = obj_ptr + 0x18
    state = dolphin_memory_engine.read_word(state_addr)
    enabled_ptr = obj_ptr + 0x10
    enabled = dolphin_memory_engine.read_byte(enabled_ptr)
    if 0 < state < 3 and enabled == 1:
        dolphin_memory_engine.write_word(state_addr, 3)
        # _set_trig_active(ctx, BALLOON_KID_SUC_TRIG_ID)


def _set_trig_active(ctx: GDLContext, trig_info: Tuple[bytes, int]):
    obj_ptr = _get_ptr_from_info(ctx, trig_info)
    if obj_ptr is None:
        return
    addr = obj_ptr + 0x7
    val = dolphin_memory_engine.read_byte(addr)
    if val & 1 != 1:
        dolphin_memory_engine.write_byte(addr, val & 1)


def _check_cur_scene(ctx: GDLContext, scene_id: bytes, scene_ptr: Optional[int] = None):
    if scene_ptr is None:
        scene_ptr = dolphin_memory_engine.read_word(CUR_SCENE_PTR_ADDR)
        if not _is_ptr_valid(scene_ptr): return False
    cur_scene = dolphin_memory_engine.read_bytes(scene_ptr, 0x4)
    return cur_scene == scene_id


def _print_player_info(ctx: GDLContext):
    base_flags = dolphin_memory_engine.read_bytes(PLAYER_ADDR + 6, 0x2)
    if base_flags != ctx.LAST_STATE[0]:
        str_1 = format(int(ctx.LAST_STATE[0].hex(), 16), '#018b')
        str_1 = f"{str_1[2:10]} {str_1[10:]}"
        str_2 = format(int(base_flags.hex(), 16), '#018b')
        str_2 = f"{str_2[2:10]} {str_2[10:]}"
        print(f"player base flags:\t{str_1}-> {str_2}")
        ctx.LAST_STATE[0] = base_flags
    ent_flags = dolphin_memory_engine.read_bytes(PLAYER_ADDR + 0x18, 0x2)
    if ent_flags != ctx.LAST_STATE[1]:
        str_1 = format(int(ctx.LAST_STATE[1].hex(), 16), '#018b')
        str_1 = f"{str_1[2:10]} {str_1[10:]}"
        str_2 = format(int(ent_flags.hex(), 16), '#018b')
        str_2 = f"{str_2[2:10]} {str_2[10:]}"
        print(f"ent_flags:\t\t\t{str_1}-> {str_2}")
        ctx.LAST_STATE[1] = ent_flags
    pflags = dolphin_memory_engine.read_bytes(PLAYER_ADDR + 0x1b, 0x2)
    if pflags != ctx.LAST_STATE[2]:
        str_1 = format(int(ctx.LAST_STATE[2].hex(), 16), '#018b')
        str_1 = f"{str_1[2:10]} {str_1[10:]}"
        str_2 = format(int(pflags.hex(), 16), '#018b')
        str_2 = f"{str_2[2:10]} {str_2[10:]}"
        print(f"pflags:\t\t\t\t{str_1}-> {str_2}")
        ctx.LAST_STATE[2] = pflags


def _give_item(ctx: GDLContext, item_id: int):
    temp = item_id - base_id
    if temp == 0:
        _give_spat(ctx)
    elif temp == 1:
        _give_sock(ctx)
    elif temp == 2:
        _give_shiny_objects(ctx, 100)
    elif temp == 3:
        _give_shiny_objects(ctx, 250)
    elif temp == 4:
        _give_shiny_objects(ctx, 500)
    elif temp == 5:
        _give_shiny_objects(ctx, 750)
    elif temp == 6:
        _give_shiny_objects(ctx, 1000)
    elif temp == 7:
        _give_powerup(ctx, 0)
    elif temp == 8:
        _give_powerup(ctx, 1)
    elif temp == 9:
        _give_golden_underwear(ctx)
    elif temp == 10:
        _give_level_pickup(ctx, 1)
    elif temp == 11:
        _give_level_pickup(ctx, 2)
    elif temp == 12:
        _give_level_pickup(ctx, 3)
        _inc_delayed_item_count(ctx, BALLOON_KID_COUNT_ADDR)
    elif temp == 13:
        _give_level_pickup(ctx, 5)
    elif temp == 14:
        _give_level_pickup(ctx, 6)
    elif temp == 15:
        _inc_delayed_item_count(ctx, SANDMAN_COUNT_ADDR)
    elif temp == 16:
        _give_level_pickup(ctx, 9)
    elif temp == 17:
        _inc_delayed_item_count(ctx, POWER_CRYSTAL_COUNT_ADDR)
    elif temp == 18:
        _give_level_pickup(ctx, 10)
        _inc_delayed_item_count(ctx, CANNON_BUTTON_COUNT_ADDR)
    else:
        logger.warning(f"Received unknown item with id {item_id}")


async def update_delayed_items(ctx: GDLContext):
    if not await check_alive(ctx):
        return
    if CheckTypes.LEVEL_ITEMS in ctx.included_check_types:
        balloon_count = dolphin_memory_engine.read_byte(BALLOON_KID_COUNT_ADDR)
        _set_counter_value(ctx, BALLOON_KID_COUNTER_ID, max(5 - balloon_count, 0))
        if balloon_count >= 5:
            _set_taskbox_success(ctx, BALLOON_KID_TASKBOX_ID)
        sandman_count = dolphin_memory_engine.read_byte(SANDMAN_COUNT_ADDR)
        _set_counter_value(ctx, SANDMAN_CNTR_ID, max(8 - sandman_count, 0))
        if sandman_count >= 8:
            _set_pickup_active(ctx, SANDMAN_SOCK_ID)
        power_crystal_count = dolphin_memory_engine.read_byte(POWER_CRYSTAL_COUNT_ADDR)
        _set_counter_value(ctx, POWERCRYSTAL_COUNTER_ID, power_crystal_count)
        if power_crystal_count >= 6:
            for v in POWERCRYSTAL_TASKBOX_IDS:
                _set_taskbox_success(ctx, v)
        cannon_button_count = dolphin_memory_engine.read_byte(CANNON_BUTTON_COUNT_ADDR)
        if cannon_button_count >= 4:
            _set_pickup_active(ctx, CANNON_BUTTON_SPAT_ID)
            _set_plat_active(ctx, CANNON_BUTTON_PLAT_IDS[0])
            _set_plat_inactive(ctx, CANNON_BUTTON_PLAT_IDS[1])
            # _set_plat_inactive(ctx, CANNON_BUTTON_PLAT_IDS[2])


async def give_items(ctx: GDLContext):
    await update_delayed_items(ctx)
    expected_idx = dolphin_memory_engine.read_word(EXPECTED_INDEX_ADDR)
    # we need to loop some items
    for item, idx in ctx.items_received_2:
        if check_control_owner(ctx, lambda owner: owner & 0x2 or owner & 0x8000 or owner & 0x200 or owner & 0x1):
            return
        if expected_idx <= idx:
            item_id = item.item
            _give_item(ctx, item_id)
            dolphin_memory_engine.write_word(EXPECTED_INDEX_ADDR, idx + 1)
            await asyncio.sleep(.01)  # wait a bit for values to update


# ToDo: do we actually want this?
# ToDo: implement socks/golden underwear/lvl_pickups/skills/ etc..
# async def set_locations(ctx: GDLContext):
#     scene_ptr = dolphin_memory_engine.read_word(CUR_SCENE_PTR_ADDR)
#     if not _is_ptr_valid(scene_ptr):
#         return
#     scene = dolphin_memory_engine.read_bytes(scene_ptr, 0x4)
#     ptr = dolphin_memory_engine.read_word(SCENE_OBJ_LIST_PTR_ADDR)
#     if not _is_ptr_valid(ptr):
#         return
#     size = dolphin_memory_engine.read_word(SCENE_OBJ_LIST_SIZE_ADDR)
#     for v in ctx.checked_locations:
#         if v not in SPAT_PICKUP_IDS.keys():
#             continue
#         val = SPAT_PICKUP_IDS[v]
#         if val[0] != scene:
#             continue
#         obj_ptr = _find_obj_in_obj_table(val[1], ptr, size)
#         if obj_ptr is None: break
#         if obj_ptr == -1: continue
#         if not _is_ptr_valid(obj_ptr + 0x16C):
#             return
#         obj_state = dolphin_memory_engine.read_word(obj_ptr + 0x16C)
#         print(obj_state)
#         if obj_state is not None and obj_state & 0x4 == 0:
#             dolphin_memory_engine.write_word(obj_ptr + 0x16c, obj_state & ~0x3f | 0x4)


def _check_pickup_state(ctx: GDLContext, obj_ptr: int):
    if not _is_ptr_valid(obj_ptr + 0x16C):
        return False
    obj_state = dolphin_memory_engine.read_word(obj_ptr + 0x16c)
    return obj_state & 0x08 > 0 and obj_state & 0x37 == 0


def _check_button_state(ctx: GDLContext, obj_ptr: int):
    if not _is_ptr_valid(obj_ptr + 0x144):
        return False
    btn_state = dolphin_memory_engine.read_word(obj_ptr + 0x144)
    return btn_state & 0x1 == 0x1


def _check_destructible_state(ctx: GDLContext, obj_ptr: int):
    if not _is_ptr_valid(obj_ptr + 0xdc):
        return False
    health = dolphin_memory_engine.read_word(obj_ptr + 0xdc)
    return health == 0


def format_to_bitmask(val: bytes) -> str:
    result = ''
    for b in val:
        result += format(b, '#010b') + ' '
    return result


def _check_platform_state(ctx: GDLContext, obj_ptr: int):
    if not _is_ptr_valid(obj_ptr + 0x18):
        return False
    state = dolphin_memory_engine.read_byte(obj_ptr + 0x18)
    return state != 1


def _check_counter(ctx: GDLContext, obj_ptr: int, target_cb: Callable):
    if not _is_ptr_valid(obj_ptr + 0x14):
        return False
    counter = int.from_bytes(dolphin_memory_engine.read_bytes(obj_ptr + 0x14, 0x2), "big")
    return target_cb(counter)


def _check_base_inactive(ctx: GDLContext, obj_ptr: int):
    if not _is_ptr_valid(obj_ptr + 0x6):
        return False
    state = dolphin_memory_engine.read_bytes(obj_ptr + 0x6, 0x2)
    return state[1] & 0x1 == 0


def _check_base_active(ctx: GDLContext, obj_ptr: int):
    return not _check_base_inactive(ctx, obj_ptr)


async def _check_objects_by_id(ctx: GDLContext, locations_checked: set, id_table: dict, check_cb: Callable):
    scene_ptr = dolphin_memory_engine.read_word(CUR_SCENE_PTR_ADDR)
    if not _is_ptr_valid(scene_ptr):
        return
    scene = dolphin_memory_engine.read_bytes(scene_ptr, 0x4)
    ptr = dolphin_memory_engine.read_word(SCENE_OBJ_LIST_PTR_ADDR)
    if not _is_ptr_valid(ptr):
        return
    size = dolphin_memory_engine.read_word(SCENE_OBJ_LIST_SIZE_ADDR)
    for k, v in id_table.items():
        if k in locations_checked and (k != base_id + 83 or ctx.finished_game):  # we need to check base_id + 83 for goal
            continue
        if v[0] is not None and v[0] != scene:
            continue
        for i in range(1, len(v)):
            obj_ptr = _find_obj_in_obj_table(v[i], ptr, size)
            if obj_ptr is None: break
            if obj_ptr == -1: continue
            if check_cb(ctx, obj_ptr):
                locations_checked.add(k)
                if k == base_id + 83 and not ctx.finished_game:
                    print("send done")
                    await ctx.send_msgs([
                        {"cmd": "StatusUpdate",
                         "status": 30}
                    ])
                    ctx.finished_game = True
                break


async def _check_spats(ctx: GDLContext, locations_checked: set):
    await _check_objects_by_id(ctx, locations_checked, SPAT_COUNTER_IDS,
                               lambda ctx, ptr: _check_counter(ctx, ptr, lambda cnt: cnt == 2))
    await _check_objects_by_id(ctx, locations_checked, SPAT_PICKUP_IDS, _check_pickup_state)


async def _check_socks(ctx: GDLContext, locations_checked: set):
    await _check_objects_by_id(ctx, locations_checked, SOCK_PICKUP_IDS, _check_pickup_state)


async def _check_golden_underwear(ctx: GDLContext, locations_checked: set):
    await _check_objects_by_id(ctx, locations_checked, GOLDEN_UNDERWEAR_IDS, _check_pickup_state)


async def _check_level_pickups(ctx: GDLContext, locations_checked: set):
    await _check_objects_by_id(ctx, locations_checked, KING_JF_DISP_ID, _check_base_active)
    await _check_objects_by_id(ctx, locations_checked, STEERING_WHEEL_PICKUP_IDS, _check_pickup_state)
    await _check_objects_by_id(ctx, locations_checked, BALLOON_KID_PLAT_IDS, _check_platform_state)
    await _check_objects_by_id(ctx, locations_checked, ART_WORK_IDS, _check_pickup_state)
    await _check_objects_by_id(ctx, locations_checked, OVERRIDE_BUTTON_IDS, _check_button_state)
    await _check_objects_by_id(ctx, locations_checked, SANDMAN_DSTR_IDS, _check_destructible_state)
    await _check_objects_by_id(ctx, locations_checked, LOST_CAMPER_TRIG_IDS, _check_base_inactive)
    await _check_objects_by_id(ctx, locations_checked, POWERCRYSTAL_PICKUP_IDS, _check_pickup_state)
    await _check_objects_by_id(ctx, locations_checked, CANNON_BUTTON_IDS, _check_button_state)


async def _check_purple_so(ctx: GDLContext, locations_checked: set):
    await _check_objects_by_id(ctx, locations_checked, PURPLE_SO_IDS, _check_pickup_state)


def _check_skills(ctx: GDLContext, locations_checked: set):
    # just check if we checked the boss spats locations
    if (base_id + 32) in locations_checked and (base_id + 234) not in locations_checked:
        locations_checked.add(base_id + 234)
    if (base_id + 57) in locations_checked and (base_id + 235) not in locations_checked:
        locations_checked.add(base_id + 235)


async def check_locations(ctx: GDLContext):
    await _check_spats(ctx, ctx.locations_checked)
    if CheckTypes.SOCK in ctx.included_check_types:
        await _check_socks(ctx, ctx.locations_checked)
    if CheckTypes.SKILLS in ctx.included_check_types:
        _check_skills(ctx, ctx.locations_checked)
    if CheckTypes.GOLDEN_UNDERWEAR in ctx.included_check_types:
        await _check_golden_underwear(ctx, ctx.locations_checked)
    if CheckTypes.LEVEL_ITEMS in ctx.included_check_types:
        await _check_level_pickups(ctx, ctx.locations_checked)
    if CheckTypes.PURPLE_SO in ctx.included_check_types:
        await _check_purple_so(ctx, ctx.locations_checked)
    # ignore already in server state
    locations_checked = ctx.locations_checked.difference(ctx.checked_locations)
    if locations_checked:
        await ctx.send_msgs([
            {"cmd": "LocationChecks",
             "locations": locations_checked}
        ])
        print([ctx.location_names[location] for location in locations_checked])


async def check_alive(ctx: GDLContext):
    cur_health = dolphin_memory_engine.read_word(HEALTH_ADDR)
    return not (cur_health <= 0 or check_control_owner(ctx, lambda owner: owner & 0x4))


async def check_death(ctx: GDLContext):
    cur_health = dolphin_memory_engine.read_word(HEALTH_ADDR)
    if cur_health <= 0 or check_control_owner(ctx, lambda owner: owner & 0x4):
        if not ctx.has_send_death and time.time() >= ctx.last_death_link + 3:
            ctx.has_send_death = True
            await ctx.send_death("GDL")
    else:
        ctx.has_send_death = False


def check_ingame(ctx: GDLContext, ignore_control_owner: bool = False) -> bool:
    scene_ptr = dolphin_memory_engine.read_word(CUR_SCENE_PTR_ADDR)
    if not _is_ptr_valid(scene_ptr):
        return False
    scene = dolphin_memory_engine.read_bytes(scene_ptr, 0x4)
    if scene not in valid_scenes:
        return False
    update_current_scene(ctx, scene.decode('ascii'))
    return True


def update_current_scene(ctx: GDLContext, scene: str):
    if not ctx.slot and not ctx.auth:
        return
    if ctx.current_scene_key is None or ctx.current_scene_key not in ctx.stored_data:
        return
    if ctx.stored_data[ctx.current_scene_key] == scene:
        return
    Utils.async_start(ctx.send_msgs([{
        "cmd": "Set",
        "key": ctx.current_scene_key,
        "default": None,
        "want_reply": True,
        "operations": [{
            "operation": "replace",
            "value": scene,
        }],
    }]))


def check_control_owner(ctx: GDLContext, check_cb: Callable[[int], bool]) -> bool:
    owner = dolphin_memory_engine.read_word(PLAYER_CONTROL_OWNER)
    return check_cb(owner)


def validate_save(ctx: GDLContext) -> bool:
    saved_slot_bytes = dolphin_memory_engine.read_bytes(SAVED_SLOT_NAME_ADDR, 0x40).strip(b'\0')
    slot_bytes = dolphin_memory_engine.read_bytes(SLOT_NAME_ADDR, 0x40).strip(b'\0')
    saved_seed_bytes = dolphin_memory_engine.read_bytes(SAVED_SEED_ADDR, 0x10).strip(b'\0')
    seed_bytes = dolphin_memory_engine.read_bytes(SEED_ADDR, 0x10).strip(b'\0')
    if len(slot_bytes) > 0 and len(seed_bytes) > 0:
        if len(saved_slot_bytes) == 0 and len(saved_seed_bytes) == 0:
            # write info to save
            dolphin_memory_engine.write_bytes(SAVED_SLOT_NAME_ADDR, slot_bytes)
            dolphin_memory_engine.write_bytes(SAVED_SEED_ADDR, seed_bytes)
            return True
        elif slot_bytes == saved_slot_bytes and seed_bytes == saved_seed_bytes:
            return True
    return False


async def dolphin_sync_task(ctx: GDLContext):
    logger.info("Starting Dolphin connector. Use /dolphin for status information")
    while not ctx.exit_event.is_set():
        try:
            if dolphin_memory_engine.is_hooked() and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                if not check_ingame(ctx):
                    # reset AP values when on main menu
                    # ToDo: this should be done via patch when other globals are reset
                    if _check_cur_scene(ctx, b'MNU3'):
                        for i in range(0, 0x80, 0x4):
                            cur_val = dolphin_memory_engine.read_word(EXPECTED_INDEX_ADDR + i)
                            if cur_val != 0:
                                dolphin_memory_engine.write_word(EXPECTED_INDEX_ADDR + i, 0)
                    await asyncio.sleep(.1)
                    continue
                # _print_player_info(ctx)
                if ctx.slot:
                    if not validate_save(ctx):
                        logger.info(CONNECTION_REFUSED_SAVE_STATUS)
                        ctx.dolphin_status = CONNECTION_REFUSED_SAVE_STATUS
                        dolphin_memory_engine.un_hook()
                        await ctx.disconnect()
                        await asyncio.sleep(5)
                        continue
                    ctx.current_scene_key = f"gdl_current_scene_T{ctx.team}_P{ctx.slot}"
                    ctx.set_notify(ctx.current_scene_key)
                    if "DeathLink" in ctx.tags:
                        await check_death(ctx)
                    await give_items(ctx)
                    await check_locations(ctx)
                    # await set_locations(ctx)
                else:
                    if not ctx.auth:
                        ctx.auth = dolphin_memory_engine.read_bytes(SLOT_NAME_ADDR, 0x40).decode('utf-8').strip(
                            '\0')
                        if ctx.auth == '\x02\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00' \
                                       '\x00\x02\x00\x00\x00\x04\x00\x00\x00\x04':
                            logger.info("Vanilla game detected. Please load the patched game.")
                            ctx.dolphin_status = CONNECTION_REFUSED_GAME_STATUS
                            ctx.awaiting_rom = False
                            dolphin_memory_engine.un_hook()
                            await ctx.disconnect()
                            await asyncio.sleep(5)
                    if ctx.awaiting_rom:
                        await ctx.server_auth()
                await asyncio.sleep(.5)
            else:
                if ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                    logger.info("Connection to Dolphin lost, reconnecting...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                logger.info("Attempting to connect to Dolphin")
                dolphin_memory_engine.hook()
                if dolphin_memory_engine.is_hooked():
                    if dolphin_memory_engine.read_bytes(0x80000000, 6) == b'GUNE5D':
                        logger.info(CONNECTION_CONNECTED_STATUS)
                        ctx.dolphin_status = CONNECTION_CONNECTED_STATUS
                        ctx.locations_checked = set()
                    else:
                        logger.info(CONNECTION_REFUSED_GAME_STATUS)
                        ctx.dolphin_status = CONNECTION_REFUSED_GAME_STATUS
                        dolphin_memory_engine.un_hook()
                        await asyncio.sleep(1)
                else:
                    logger.info("Connection to Dolphin failed, attempting again in 5 seconds...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                    await ctx.disconnect()
                    await asyncio.sleep(5)
                    continue
        except Exception:
            dolphin_memory_engine.un_hook()
            logger.info("Connection to Dolphin failed, attempting again in 5 seconds...")
            logger.error(traceback.format_exc())
            ctx.dolphin_status = CONNECTION_LOST_STATUS
            await ctx.disconnect()
            await asyncio.sleep(5)
            continue


async def patch_and_run_game(ctx: GDLContext, patch_file):
    try:
        result_path = os.path.splitext(patch_file)[0] + GDLDeltaPatch.result_file_ending
        with zipfile.ZipFile(patch_file, 'r') as patch_archive:
            if not GDLDeltaPatch.check_version(patch_archive):
                logger.error(
                    "apgdl version doesn't match this client.  Make sure your generator and client are the same")
                raise Exception("apgdl version doesn't match this client.")

        # check hash
        GDLDeltaPatch.check_hash()

        shutil.copy(GDLDeltaPatch.get_rom_path(), result_path)
        await GDLDeltaPatch.apply_hiphop_changes(zipfile.ZipFile(patch_file, 'r'), GDLDeltaPatch.get_rom_path(),
                                                  result_path)
        await GDLDeltaPatch.apply_binary_changes(zipfile.ZipFile(patch_file, 'r'), result_path)

        logger.info('--patching success--')
        os.startfile(result_path)

    except Exception as msg:
        logger.info(msg, extra={'compact_gui': True})
        logger.debug(traceback.format_exc())
        ctx.gui_error('Error', msg)


def main(connect=None, password=None, patch_file=None):
    # Text Mode to use !hint and such with games that have no text entry
    Utils.init_logging("GDLClient")

    # logger.warning(f"starting {connect}, {password}, {patch_file}")

    async def _main(connect, password, patch_file):
        ctx = GDLContext(connect, password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        ctx.patch_task = None
        if patch_file:
            ext = os.path.splitext(patch_file)[1]
            if ext == GDLDeltaPatch.patch_file_ending:
                logger.info("apgdl file supplied, beginning patching process...")
                ctx.patch_task = asyncio.create_task(patch_and_run_game(ctx, patch_file), name="PatchGame")
            elif ext == GDLDeltaPatch.result_file_ending:
                os.startfile(patch_file)
            else:
                logger.warning(f"Unknown patch file extension {ext}")

        if ctx.patch_task:
            await ctx.patch_task

        await asyncio.sleep(1)

        ctx.dolphin_sync_task = asyncio.create_task(dolphin_sync_task(ctx), name="DolphinSync")

        await ctx.exit_event.wait()
        ctx.server_address = None

        await ctx.shutdown()

        if ctx.dolphin_sync_task:
            await asyncio.sleep(3)
            await ctx.dolphin_sync_task

    import colorama

    colorama.init()
    asyncio.run(_main(connect, password, patch_file))
    colorama.deinit()


if __name__ == '__main__':
    parser = get_base_parser()
    parser.add_argument('patch_file', default="", type=str, nargs="?",
                        help='Path to an .apgdl patch file')
    args = parser.parse_args()
    main(args.connect, args.password, args.patch_file)
