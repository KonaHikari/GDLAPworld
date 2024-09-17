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
    Base = 1
    Region_Key = 2



CONNECTION_REFUSED_GAME_STATUS = "Dolphin Connection refused due to invalid Game. Please load the US Version of GDL."
CONNECTION_REFUSED_SAVE_STATUS = "Dolphin Connection refused due to invalid Save. " \
                                 "Please make sure you loaded a save file used on this slot and seed."
CONNECTION_LOST_STATUS = "Dolphin Connection was lost. Please restart your emulator and make sure GDL is running."
CONNECTION_CONNECTED_STATUS = "Dolphin Connected"
CONNECTION_INITIAL_STATUS = "Dolphin Connection has not been initiated"

CUR_SCENE_PTR_ADDR = 0x80257738 #could be 802583b3 or 8028c9b4

GLOBALS_ADDR = 0X8027

HEALTH_ADDR = 0x80277994

LW_INV_ADDRESS = 0X802768b8, 0X802769A8, GLOBALS_ADDR + 0X6A98, GLOBALS_ADDR + 0X6B88, \
      GLOBALS_ADDR + 0X6C78, GLOBALS_ADDR + 0X6D68, GLOBALS_ADDR + 0X6E58, GLOBALS_ADDR + 0X6F48

RK_MK_ITEM_ADDR = 0X802768D2, 0X802769C2, GLOBALS_ADDR + 0X6AB2, GLOBALS_ADDR + 0X6BA2, \
      GLOBALS_ADDR + 0X6C92, GLOBALS_ADDR + 0X6D82, GLOBALS_ADDR + 0X6E72, GLOBALS_ADDR + 0X6F62
RK_CS_ITEM_ADDR = 0X802768D4, 0X802769C4, GLOBALS_ADDR + 0X6AB4, GLOBALS_ADDR + 0X6BA4, \
      GLOBALS_ADDR + 0X6C94, GLOBALS_ADDR + 0X6D84, GLOBALS_ADDR + 0X6E74, GLOBALS_ADDR + 0X6F64
RK_SD_ITEM_ADDR = 0X802768D6, 0X802769C6, GLOBALS_ADDR + 0X6AB6, GLOBALS_ADDR + 0X6BA6, \
      GLOBALS_ADDR + 0X6C96, GLOBALS_ADDR + 0X6D86, GLOBALS_ADDR + 0X6E76, GLOBALS_ADDR + 0X6F66
RK_FR_ITEM_ADDR = 0X802768D8, 0X802769C8, GLOBALS_ADDR + 0X6AB8, GLOBALS_ADDR + 0X6BA8, \
      GLOBALS_ADDR + 0X6C98, GLOBALS_ADDR + 0X6D88, GLOBALS_ADDR + 0X6E78, GLOBALS_ADDR + 0X6F68
RK_DL_ITEM_ADDR = 0X802768DA, 0X802769CA, GLOBALS_ADDR + 0X6ABA, GLOBALS_ADDR + 0X6BAA, \
      GLOBALS_ADDR + 0X6C9A, GLOBALS_ADDR + 0X6D8A, GLOBALS_ADDR + 0X6E7A, GLOBALS_ADDR + 0X6F6A
RK_ID_ITEM_ADDR = 0X802768DC, 0X802769CC, GLOBALS_ADDR + 0X6ABC, GLOBALS_ADDR + 0X6BAC, \
      GLOBALS_ADDR + 0X6C9C, GLOBALS_ADDR + 0X6D8C, GLOBALS_ADDR + 0X6E7C, GLOBALS_ADDR + 0X6F6C
RK_DW_ITEM_ADDR = 0X802768DE, 0X802769CE, GLOBALS_ADDR + 0X6ABE, GLOBALS_ADDR + 0X6BAE, \
      GLOBALS_ADDR + 0X6C9E, GLOBALS_ADDR + 0X6D8E, GLOBALS_ADDR + 0X6E7E, GLOBALS_ADDR + 0X6F6E
W_WING_ITEM_ADDR = 0X802768C8, 0X802769B8, GLOBALS_ADDR + 0X6AA8, GLOBALS_ADDR + 0X6B98, \
      GLOBALS_ADDR + 0X6C88, GLOBALS_ADDR + 0X6D78, GLOBALS_ADDR + 0X6D78, GLOBALS_ADDR + 0X6F58
E_WING_ITEM_ADDR = 0X802768CA, 0X802769BA, GLOBALS_ADDR + 0X6AAA, GLOBALS_ADDR + 0X6B9A, \
      GLOBALS_ADDR + 0X6C8A, GLOBALS_ADDR + 0X6D7A, GLOBALS_ADDR + 0X6D7A, GLOBALS_ADDR + 0X6F5A
L_TOWER_ITEM_ADDR = 0X802768CC, 0X802769BC, GLOBALS_ADDR + 0X6AAC, GLOBALS_ADDR + 0X6B9C, \
      GLOBALS_ADDR + 0X6C8C, GLOBALS_ADDR + 0X6D7C, GLOBALS_ADDR + 0X6D7C, GLOBALS_ADDR + 0X6F5C

EXP_ADDRESS=0x802779A0 #need to implement for Double exp. 

# AP free space usage
# notes on free space
# 0x817FFFF6 - 0x817FFFFF
# around 0x8179f890-0x817fcf00 (?)

# @0x817f0080 save game write injection code
# @0x817f0400 save game read injection code



SLOT_NAME_ADDR = 0x8028F2a0
SEED_ADDR = SLOT_NAME_ADDR + 0x40
# we could extend up to 0x80 bytes or more if we move AP code from 0x817f0080 to somewhere else
# expected received item index
EXPECTED_INDEX_ADDR = 0x817f0000  #that's for keeping track of the index from received items, that will be saved with the save file so you don't get all items again everytime you connect (not my address, maybe needs changed)
SAVED_SLOT_NAME_ADDR = 0x8012A7D4
SAVED_SEED_ADDR = SAVED_SLOT_NAME_ADDR + 0x40
# delayed item
# some custom code at 0x817f0080



base_id = 5240216

RUNES_PICKUP_IDS = {
    (base_id + 0): (b'G1', 0x811f1aa4),  # poison field runestone
    (base_id + 1): (b'G4', 0x814396e8),  # mausoleum runestone
    (base_id + 8): (b'B1', 0x8137acf4),  # peaks runestone
    (base_id + 16): (b'A4', 0x814e3db4),  # armory runestone
    (base_id + 24): (b'K2', 0x8137fb94),  # cloud docks runestone
    (base_id + 25): (b'K4', 0x812ac844),  # mothership
    (base_id + 32): (b'D2', 0x813ff5c4),  # twisted roots
    (base_id + 33): (b'C1', 0x81357734),  # city ruins
    (base_id + 41): (b'I2', 0x8135DD64),  # frozen camp
    (base_id + 42): (b'I3', 0x812752B4),  # crystal mine
    (base_id + 49): (b'J4', 0x8139D2A4),  # nightmare
    (base_id + 50): (b'J5', 0x814FA784),  # maze
    (base_id + 57): (b'H3', 0x81357954),  # fortress
}

# (item name, scene id, id)
BOSS_PICKUP_IDS = {
    (base_id + 100+0): (b'G5', 0x802416b4), #Lich
    (base_id + 100+1): (b'B6', 0x802416b4), #Dragon
    (base_id + 100+2): (b'A6', 0x802416b4), #Chimera
    (base_id + 100+3): (b'K5', 0x802416b4), #Plague Fiend 
    (base_id + 100+4): (b'D5', 0x802416b4), #Spider Queen
    (base_id + 100+5): (b'C5', 0x802416b4), #Genie
    (base_id + 100+6): (b'I5', 0x802416b4), #Yeti
    (base_id + 100+7): (b'J6', 0x802416b4), #Wraith
    (base_id + 100+8): (b'E2', 0x802416b4), #Skorne 1
    (base_id + 100+9): (b'F2', 0x802416b4), #Skorne 2
}
LW_PICKUP_IDS = {
    (base_id + 183 + 0): (b'G3', 0x811edc24), #Parchment of Fire
    (base_id + 183 + 1): (b'B5', 0x81324d04), #Javelin of Blinding
    (base_id + 183 + 2): (b'A3', 0x81465be4), #Ice Axe
    (base_id + 183 + 3): (b'K3', 0x81265ee4), #The Good Book
    (base_id + 183 + 4): (b'D4', 0x814134F4), #Scimitar
    (base_id + 183 + 5): (b'C3', 0x812FF544), #Toxic Bellows
    (base_id + 183 + 6): (b'I4', 0x8143FC14), #Lamp
    (base_id + 183 + 7): (b'J2', 0x81326754), #Lantern
    (base_id + 183 + 8): (b'E1', 0x8114D134), #Soul Savior
}

TREASURE_ROOMS_PICKUP_IDS = {
    (base_id + 210 + 1): (b'S8', 0x80276413),  # Medusa
    (base_id + 210 + 2): (b'S4', 0x80276413),  # Minotaur
    (base_id + 210 + 3): (b'S3', 0x80276413),  # Falconess
    (base_id + 210 + 4): (b'S9', 0x80276413),  # Unicorn
    (base_id + 210 + 5): (b'S2', 0x80276413),  # tirgress
    (base_id + 210 + 6): (b'S1', 0x80276413),  # jackal
    (base_id + 210 + 7): (b'S6', 0x80276413),  # ogre
    (base_id + 210 + 8): (b'S7', 0x80276413),  # hyena
    (base_id + 210 + 9): (b'S5', 0x80276413),  # sumner
    

}
REGION_KEY_PICKUP_IDS = {
    (base_id + 216 + 1): (None, 0x802768d1, GLOBALS_ADDR + 0x69C1, GLOBALS_ADDR + 0x6AB1, GLOBALS_ADDR + 0x6BA1, GLOBALS_ADDR + 0x6C91, GLOBALS_ADDR + 0x6D81, GLOBALS_ADDR + 0x6E71, GLOBALS_ADDR + 0x6F61),  # All FP crystals 
    (base_id + 216 + 2): (None, 0x802768d3, GLOBALS_ADDR + 0x69C3, GLOBALS_ADDR + 0x6AB3, GLOBALS_ADDR + 0x6BA3, GLOBALS_ADDR + 0x6C93, GLOBALS_ADDR + 0x6D83, GLOBALS_ADDR + 0x6E73, GLOBALS_ADDR + 0x6F63),  # All MK crystals
    (base_id + 216 + 3): (None, 0x802768d5, GLOBALS_ADDR + 0x69C5, GLOBALS_ADDR + 0x6AB5, GLOBALS_ADDR + 0x6BA5, GLOBALS_ADDR + 0x6C95, GLOBALS_ADDR + 0x6D85, GLOBALS_ADDR + 0x6E75, GLOBALS_ADDR + 0x6F65),  # All CS crystals
    (base_id + 216 + 4): (None, 0x802768d7, GLOBALS_ADDR + 0x69C7, GLOBALS_ADDR + 0x6AB7, GLOBALS_ADDR + 0x6BA7, GLOBALS_ADDR + 0x6C97, GLOBALS_ADDR + 0x6D87, GLOBALS_ADDR + 0x6E77, GLOBALS_ADDR + 0x6F67),  # All SD crystals
    (base_id + 216 + 5): (None, 0x802768d9, GLOBALS_ADDR + 0x69C9, GLOBALS_ADDR + 0x6AB9, GLOBALS_ADDR + 0x6BA9, GLOBALS_ADDR + 0x6C99, GLOBALS_ADDR + 0x6D89, GLOBALS_ADDR + 0x6E79, GLOBALS_ADDR + 0x6F69),  # All FR crystals
    (base_id + 216 + 6): (None, 0x802768dB, GLOBALS_ADDR + 0x69CB, GLOBALS_ADDR + 0x6ABB, GLOBALS_ADDR + 0x6BAB, GLOBALS_ADDR + 0x6C9B, GLOBALS_ADDR + 0x6D8B, GLOBALS_ADDR + 0x6E7B, GLOBALS_ADDR + 0x6F6B),  # All DL crystals
    (base_id + 216 + 7): (None, 0x802768dD, GLOBALS_ADDR + 0x69CD, GLOBALS_ADDR + 0x6ABD, GLOBALS_ADDR + 0x6BAD, GLOBALS_ADDR + 0x6C9D, GLOBALS_ADDR + 0x6D8D, GLOBALS_ADDR + 0x6E7D, GLOBALS_ADDR + 0x6F6D),  # All ID crystals
    (base_id + 216 + 8): (None, 0x802768dF, GLOBALS_ADDR + 0x69CF, GLOBALS_ADDR + 0x6ABF, GLOBALS_ADDR + 0x6BAF, GLOBALS_ADDR + 0x6C9F, GLOBALS_ADDR + 0x6D8F, GLOBALS_ADDR + 0x6E7F, GLOBALS_ADDR + 0x6F6F),  # All DW crystals

    

}



valid_scenes = [
    b'A1', b'A2', b'A3', b'A4', b'A5', b'A6', 
    b'B1', b'B2', b'B3', b'B4', b'B5', b'B6',
    b'C1', b'C2', b'C3', b'C4', b'C5',
    b'D1', b'D2', b'D3', b'D4', b'D5',
    b'E1', b'E2',
    b'F1', b'F2',
    b'G1', b'G2', b'G3', b'G4', b'G5',
    b'H1', b'H2', b'H3', b'H4',
    b'I1', b'I2', b'I3', b'I4', b'I5',
    b'J1', b'J2', b'J3', b'J4', b'J5', b'J6',
    b'K1', b'K2', b'K3', b'K4', b'K5',
    b'L1',
    b'S1', b'S2', b'S3', b'S4', b'S5', b'S6', b'S7', b'S8', b'S9',
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
        self.included_check_types: CheckTypes = CheckTypes.Base
        self.items_received_2 = []
        self.dolphin_sync_task = None
        self.dolphin_status = CONNECTION_INITIAL_STATUS
        self.awaiting_rom = False
        self.given_socks = 0
        self.lw_count = 0
        self.rune_count = 0
        self.rk_mk_count = 0
        self.rk_cs_count = 0
        self.rk_sd_count = 0
        self.rk_fr_count = 0
        self.rk_dl_count = 0
        self.rk_id_count = 0
        self.rk_dw_count = 0
        self.wk_ww_count = 0
        self.wk_ew_count = 0
        self.wk_lt_count = 0
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
            if 'death_link' in args['slot_data']:
                Utils.async_start(self.update_death_link(bool(args['slot_data']['death_link'])))
            if 'randomize_world_order' in args['slot_data'] and args['slot_data']['randomize_world_order']:
                self.included_check_types = CheckTypes.Region_Key
        if cmd == 'ReceivedItems':
            if args["index"] >= self.last_rev_index:
                self.last_rev_index = args["index"]
                for item in args['items']:
                    self.items_received_2.append((item, self.last_rev_index))
                    self.last_rev_index += 1
            self.items_received_2.sort(key=lambda v: v[1])


    def on_deathlink(self, data: Dict[str, Any]) -> None:
        super().on_deathlink(data)
        _give_death(self)

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            logger.info('Enter the password required to join this game:')
            self.password = await self.console_input()
            return self.password
        if not self.auth:
            if self.awaiting_rom:
                return
            self.awaiting_rom = True
            logger.info('Awaiting save file to get player information')
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



def _give_lw_fp(ctx: GDLContext):
    cur_lw_count = dolphin_memory_engine.read_word(LW_INV_ADDRESS)
    dolphin_memory_engine.write_word(LW_INV_ADDRESS, cur_lw_count + 8388608)
    if cur_lw_count > ctx.lw_count:
        logger.info("!Something went wrong with the legendary weapon inventory!")

def _give_lw_mk(ctx: GDLContext):
    cur_lw_count = dolphin_memory_engine.read_word(LW_INV_ADDRESS)
    dolphin_memory_engine.write_word(LW_INV_ADDRESS, cur_lw_count + 262144)
    if cur_lw_count > ctx.lw_count:
        logger.info("!Something went wrong with the legendary weapon inventory!")

def _give_lw_cs(ctx: GDLContext):
    cur_lw_count = dolphin_memory_engine.read_word(LW_INV_ADDRESS)
    dolphin_memory_engine.write_word(LW_INV_ADDRESS, cur_lw_count + 131072)
    if cur_lw_count > ctx.lw_count:
        logger.info("!Something went wrong with the legendary weapon inventory!")

def _give_lw_sd(ctx: GDLContext):
    cur_lw_count = dolphin_memory_engine.read_word(LW_INV_ADDRESS)
    dolphin_memory_engine.write_word(LW_INV_ADDRESS, cur_lw_count + 134217728)
    if cur_lw_count > ctx.lw_count:
        logger.info("!Something went wrong with the legendary weapon inventory!")

def _give_lw_fr(ctx: GDLContext):
    cur_lw_count = dolphin_memory_engine.read_word(LW_INV_ADDRESS)
    dolphin_memory_engine.write_word(LW_INV_ADDRESS, cur_lw_count + 1048576)
    if cur_lw_count > ctx.lw_count:
        logger.info("!Something went wrong with the legendary weapon inventory!")

def _give_lw_dl(ctx: GDLContext):
    cur_lw_count = dolphin_memory_engine.read_word(LW_INV_ADDRESS)
    dolphin_memory_engine.write_word(LW_INV_ADDRESS, cur_lw_count + 524288)
    if cur_lw_count > ctx.lw_count:
        logger.info("!Something went wrong with the legendary weapon inventory!")

def _give_lw_id(ctx: GDLContext):
    cur_lw_count = dolphin_memory_engine.read_word(LW_INV_ADDRESS)
    dolphin_memory_engine.write_word(LW_INV_ADDRESS, cur_lw_count + 33554432)
    if cur_lw_count > ctx.lw_count:
        logger.info("!Something went wrong with the legendary weapon inventory!")

def _give_lw_dw(ctx: GDLContext):
    cur_lw_count = dolphin_memory_engine.read_word(LW_INV_ADDRESS)
    dolphin_memory_engine.write_word(LW_INV_ADDRESS, cur_lw_count + 67108864)
    if cur_lw_count > ctx.lw_count:
        logger.info("!Something went wrong with the legendary weapon inventory!")

def _give_lw_dt(ctx: GDLContext):
    cur_lw_count = dolphin_memory_engine.read_word(LW_INV_ADDRESS)
    dolphin_memory_engine.write_word(LW_INV_ADDRESS, cur_lw_count + 2097152)
    if cur_lw_count > ctx.lw_count:
        logger.info("!Something went wrong with the legendary weapon inventory!")

def _give_yr_1(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 128)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_yr_2(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 256)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_yr_3(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 64)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_rd_1(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 8)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")
        
def _give_rd_2(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 16)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_rd_3(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 32)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_bl_1(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 1)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")
        
def _give_bl_2(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 2)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_bl_3(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 4)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_gn_1(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 512)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")
        
def _give_gn_2(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 1024)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_gn_3(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 2048)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_bf_13(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 4096)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_shard_fp(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 4096)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_shard_mk(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 4096)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_shard_cs(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 4096)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_shard_sd(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 4096)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_shard_fr(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 4096)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_shard_dl(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 4096)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_shard_id(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 4096)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_shard_dw(ctx: GDLContext):
    cur_rune_count = dolphin_memory_engine.read_word(0x802779A8)
    dolphin_memory_engine.write_word(0x802779A8, cur_rune_count + 4096)
    if cur_rune_count > ctx.rune_count:
        logger.info("!Something went wrong with the runestone/shard inventory!")

def _give_rk_mk(ctx: GDLContext):
    cur_rk_mk_count = dolphin_memory_engine.read_word(RK_MK_ITEM_ADDR)
    dolphin_memory_engine.write_word(RK_MK_ITEM_ADDR, cur_rk_mk_count + 255)
    if cur_rk_mk_count > ctx.rk_mk_count:
        logger.info("!Some went wrong with the Mountain Kingdom count!")

def _give_rk_cs(ctx: GDLContext):
    cur_rk_cs_count = dolphin_memory_engine.read_word(RK_CS_ITEM_ADDR)
    dolphin_memory_engine.write_word(RK_CS_ITEM_ADDR, cur_rk_cs_count + 255)
    if cur_rk_cs_count > ctx.rk_cs_count:
        logger.info("!Some went wrong with the Castle Stronghold count!")

def _give_rk_sd(ctx: GDLContext):
    cur_rk_sd_count = dolphin_memory_engine.read_word(RK_SD_ITEM_ADDR)
    dolphin_memory_engine.write_word(RK_SD_ITEM_ADDR, cur_rk_sd_count + 255)
    if cur_rk_sd_count > ctx.rk_sd_count:
        logger.info("!Some went wrong with the Sky Dominion count!")

def _give_rk_fr(ctx: GDLContext):
    cur_rk_fr_count = dolphin_memory_engine.read_word(RK_FR_ITEM_ADDR)
    dolphin_memory_engine.write_word(RK_FR_ITEM_ADDR, cur_rk_fr_count + 255)
    if cur_rk_fr_count > ctx.rk_fr_count:
        logger.info("!Some went wrong with the Forest Realm count!")

def _give_rk_dl(ctx: GDLContext):
    cur_rk_dl_count = dolphin_memory_engine.read_word(RK_DL_ITEM_ADDR)
    dolphin_memory_engine.write_word(RK_DL_ITEM_ADDR, cur_rk_dl_count + 255)
    if cur_rk_dl_count > ctx.rk_dl_count:
        logger.info("!Some went wrong with the Desert Land count!")

def _give_rk_id(ctx: GDLContext):
    cur_rk_id_count = dolphin_memory_engine.read_word(RK_ID_ITEM_ADDR)
    dolphin_memory_engine.write_word(RK_ID_ITEM_ADDR, cur_rk_id_count + 255)
    if cur_rk_id_count > ctx.rk_id_count:
        logger.info("!Some went wrong with the Ice Domain count!")

def _give_rk_dw(ctx: GDLContext):
    cur_rk_dw_count = dolphin_memory_engine.read_word(RK_DW_ITEM_ADDR)
    dolphin_memory_engine.write_word(RK_DW_ITEM_ADDR, cur_rk_dw_count + 255)
    if cur_rk_dw_count > ctx.rk_dw_count:
        logger.info("!Some went wrong with the Dream World count!")

def _give_w_wing_key(ctx: GDLContext):
    cur_wk_ww_count = dolphin_memory_engine.read_word(W_WING_ITEM_ADDR)
    dolphin_memory_engine.write_word(W_WING_ITEM_ADDR, cur_wk_ww_count + 255)
    if cur_wk_ww_count > ctx.wk_ww_count:
        logger.info("!Some went wrong with the West Wing count!")

def _give_e_wing_key(ctx: GDLContext):
    cur_wk_ew_count = dolphin_memory_engine.read_word(E_WING_ITEM_ADDR)
    dolphin_memory_engine.write_word(E_WING_ITEM_ADDR, cur_wk_ew_count + 255)
    if cur_wk_ew_count > ctx.wk_ew_count:
        logger.info("!Some went wrong with the East Wing count!")

def _give_lower_key(ctx: GDLContext):
    cur_wk_lt_count = dolphin_memory_engine.read_word(L_TOWER_ITEM_ADDR)
    dolphin_memory_engine.write_word(L_TOWER_ITEM_ADDR, cur_wk_lt_count + 255)
    if cur_wk_lt_count > ctx.wk_lt_count:
        logger.info("!Some went wrong with the Lower Tower count!")

def _give_death(ctx: GDLContext):
    if ctx.slot and dolphin_memory_engine.is_hooked() and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS \
            and check_ingame(ctx):
        dolphin_memory_engine.write_word(HEALTH_ADDR, 0)


def _check_cur_scene(ctx: GDLContext, scene_id: bytes, scene_ptr: Optional[int] = None):
    if scene_ptr is None:
        scene_ptr = dolphin_memory_engine.read_word(CUR_SCENE_PTR_ADDR)
        if not _is_ptr_valid(scene_ptr): return False
    cur_scene = dolphin_memory_engine.read_bytes(scene_ptr, 0x2)
    return cur_scene == scene_id



def _give_item(ctx: GDLContext, item_id: int):
    temp = item_id - base_id
    if temp == 0:
        _give_yr_1(ctx)
    elif temp == 1:
        _give_yr_2(ctx)
    elif temp == 2:
        _give_yr_3(ctx, 100)
    elif temp == 3:
        _give_rd_1(ctx, 250)
    elif temp == 4:
        _give_rd_2(ctx, 500)
    elif temp == 5:
        _give_rd_3(ctx, 750)
    elif temp == 6:
        _give_bl_1(ctx, 1000)
    elif temp == 7:
        _give_bl_2(ctx, 0)
    elif temp == 8:
        _give_bl_3(ctx, 1)
    elif temp == 9:
        _give_gn_1(ctx)
    elif temp == 10:
        _give_gn_2(ctx, 1)
    elif temp == 11:
        _give_gn_3(ctx, 2)
    elif temp == 12:
        _give_bf_13(ctx, 3)
    elif temp == 13:
        _give_shard_fp(ctx, 5)
    elif temp == 14:
        _give_shard_mk(ctx, 6)
    elif temp == 15:
        _give_shard_cs(ctx, 7)
    elif temp == 16:
        _give_shard_sd(ctx, 8)
    elif temp == 17:
        _give_shard_fr(ctx, 9)
    elif temp == 18:
        _give_shard_dl(ctx, 10)
    elif temp == 19:
        _give_shard_id(ctx, 11)
    elif temp == 20:
        _give_shard_dw(ctx, 12)      
    elif temp == 25:
        _give_lw_fp(ctx, 13)  
    elif temp == 21:
        _give_lw_mk(ctx, 14)      
    elif temp == 22:
        _give_lw_cs(ctx, 15)  
    elif temp == 23:
        _give_lw_sd(ctx, 16)  
    elif temp == 24:
        _give_lw_fr(ctx, 17)  
    elif temp == 26:
        _give_lw_dl(ctx, 18)  
    elif temp == 27:
        _give_lw_id(ctx, 19)  
    elif temp == 28:
        _give_lw_dw(ctx, 20)  
    elif temp == 29:
        _give_lw_dt(ctx, 21)  
    elif temp == 38:
        _give_w_wing_key(ctx, 29)     
    elif temp == 39:
        _give_e_wing_key(ctx, 30)   
    elif temp == 40:
        _give_lower_key(ctx, 31)   
    elif temp == 30:
        _give_rk_mk(ctx, 22)      
    elif temp == 31:
        _give_rk_cs(ctx, 23)    
    elif temp == 32:
        _give_rk_sd(ctx, 24)    
    elif temp == 33:
        _give_rk_fr(ctx, 25)    
    elif temp == 34:
        _give_rk_dl(ctx, 26)    
    elif temp == 35:
        _give_rk_id(ctx, 27)    
    elif temp == 36:
        _give_rk_dw(ctx, 28)    
    else:
        logger.warning(f"Received unknown item with id {item_id}")


async def update_delayed_items(ctx: GDLContext):
    if not await check_alive(ctx):
        return



async def give_items(ctx: GDLContext):
    await update_delayed_items(ctx)
    expected_idx = dolphin_memory_engine.read_word(EXPECTED_INDEX_ADDR)
    # we need to loop some items
    for item, idx in ctx.items_received_2:
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
    obj_state = dolphin_memory_engine.read_word(0x811F1AA4)  # maybe 8123D7AC? test for first runestone location ID
    return obj_state  == 0



def format_to_bitmask(val: bytes) -> str:
    result = ''
    for b in val:
        result += format(b, '#010b') + ' '
    return result



async def _check_objects_by_id(ctx: GDLContext, locations_checked: set, id_table: dict, check_cb: Callable):
    scene_ptr = dolphin_memory_engine.read_word(CUR_SCENE_PTR_ADDR)
    if not _is_ptr_valid(scene_ptr):
        return
    scene = dolphin_memory_engine.read_bytes(scene_ptr, 0x2)
    for k, v in id_table.items():
        if k in locations_checked and (k != base_id + 83 or ctx.finished_game):  # we need to check base_id + 83 for goal
            continue
        if v[0] is not None and v[0] != scene:
            continue



async def _check_base(ctx: GDLContext, locations_checked: set):
    await _check_objects_by_id(ctx, locations_checked, RUNES_PICKUP_IDS, _check_pickup_state)
    await _check_objects_by_id(ctx, locations_checked, BOSS_PICKUP_IDS, _check_pickup_state)
    await _check_objects_by_id(ctx, locations_checked, LW_PICKUP_IDS, _check_pickup_state)
    await _check_objects_by_id(ctx, locations_checked, TREASURE_ROOMS_PICKUP_IDS, _check_pickup_state)
    await _check_objects_by_id(ctx, locations_checked, RUNES_PICKUP_IDS, _check_pickup_state)


async def _check_rk(ctx: GDLContext, locations_checked: set):
    await _check_objects_by_id(ctx, locations_checked, REGION_KEY_PICKUP_IDS, _check_pickup_state)


async def check_locations(ctx: GDLContext):
    await _check_base(ctx, ctx.locations_checked)
    if CheckTypes.Region_Key in ctx.included_check_types:
        await _check_rk(ctx, ctx.locations_checked)
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
    return not (cur_health <= 0)


async def check_death(ctx: GDLContext):
    cur_health = dolphin_memory_engine.read_word(HEALTH_ADDR)
    if cur_health <= 0:
        if not ctx.has_send_death and time.time() >= ctx.last_death_link + 3:
            ctx.has_send_death = True
            await ctx.send_death("GDL")
    else:
        ctx.has_send_death = False


def check_ingame(ctx: GDLContext, ignore_control_owner: bool = False) -> bool:
    scene_ptr = dolphin_memory_engine.read_word(CUR_SCENE_PTR_ADDR)
    if not _is_ptr_valid(scene_ptr):
        return False
    scene = dolphin_memory_engine.read_bytes(scene_ptr, 0x2)
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
                    if _check_cur_scene(ctx, b'L1'):
                        for i in range(0, 0x80, 0x4):
                            cur_val = dolphin_memory_engine.read_word(EXPECTED_INDEX_ADDR + i)
                            if cur_val != 0:
                                dolphin_memory_engine.write_word(EXPECTED_INDEX_ADDR + i, 0)
                    await asyncio.sleep(.1)
                    continue
                # _print_player_info(ctx)
                if ctx.slot:
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
