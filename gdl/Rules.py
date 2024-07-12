import typing
from typing import Callable, Dict, List, Tuple

from BaseClasses import MultiWorld, CollectionState, Entrance
from worlds.AutoWorld import LogicMixin
from . import GDLOptions
from .names import ConnectionNames, ItemNames, LocationNames, RegionNames
from worlds.generic.Rules import set_rule, add_rule, CollectionRule


#fix uw access. lower not needed, only runestones from hub1
base_rules = [
    # connections
    {
        ConnectionNames.lower_uw00: lambda player: lambda state: state.has(ItemNames.yr_1, player) and \
                state.has(ItemNames.yr_2, player) and \
                state.has(ItemNames.yr_3, player) and \
                state.has(ItemNames.gn_1, player) and \
                state.has(ItemNames.gn_2, player) and \
                state.has(ItemNames.gn_3, player) and \
                state.has(ItemNames.bl_1, player) and \
                state.has(ItemNames.bl_2, player) and \
                state.has(ItemNames.bl_3, player) and \
                state.has(ItemNames.rd_1, player) and \
                state.has(ItemNames.rd_2, player) and \
                state.has(ItemNames.rd_3, player),
        ConnectionNames.bf00_bf04: lambda player: lambda state: state.has(ItemNames.yr_1, player) and \
                state.has(ItemNames.yr_2, player) and \
                state.has(ItemNames.yr_3, player) and \
                state.has(ItemNames.gn_1, player) and \
                state.has(ItemNames.gn_2, player) and \
                state.has(ItemNames.gn_3, player) and \
                state.has(ItemNames.bl_1, player) and \
                state.has(ItemNames.bl_2, player) and \
                state.has(ItemNames.bl_3, player) and \
                state.has(ItemNames.rd_1, player) and \
                state.has(ItemNames.rd_2, player) and \
                state.has(ItemNames.rd_3, player) and \
                state.has(ItemNames.bf_13, player),
        ConnectionNames.hub1_dt: lambda player: lambda state: state.has(ItemNames.shard_fp, player) and \
                state.has(ItemNames.shard_mk, player) and \
                state.has(ItemNames.shard_cs, player) and \
                state.has(ItemNames.shard_sd, player) and \
                state.has(ItemNames.shard_fr, player) and \
                state.has(ItemNames.shard_dl, player) and \
                state.has(ItemNames.shard_id, player) and \
                state.has(ItemNames.shard_dw, player),
    
        ConnectionNames.hub1_west: lambda player: lambda state: state.has(ItemNames.w_wing_key, player),
        ConnectionNames.hub1_east: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
        ConnectionNames.hub1_lower: lambda player: lambda state: state.has(ItemNames.l_tower_key, player),
        ConnectionNames.lower_bf00: lambda player: lambda state: state.has(ItemNames.yr_1, player) and \
                state.has(ItemNames.yr_2, player) and \
                state.has(ItemNames.yr_3, player) and \
                state.has(ItemNames.gn_1, player) and \
                state.has(ItemNames.gn_2, player) and \
                state.has(ItemNames.gn_3, player) and \
                state.has(ItemNames.bl_1, player) and \
                state.has(ItemNames.bl_2, player) and \
                state.has(ItemNames.bl_3, player) and \
                state.has(ItemNames.rd_1, player) and \
                state.has(ItemNames.rd_2, player) and \
                state.has(ItemNames.rd_3, player) 
    #region key rules

       
    },
    # locations
    {ItemNames.runes: {
            LocationNames.runes_cs_01: lambda player: lambda state: state.has(ItemNames.w_wing_key, player),
            LocationNames.runes_sd_01: lambda player: lambda state: state.has(ItemNames.w_wing_key, player),
            LocationNames.runes_sd_02: lambda player: lambda state: state.has(ItemNames.w_wing_key, player),
            LocationNames.runes_fr_01: lambda player: lambda state: state.has(ItemNames.w_wing_key, player),
            LocationNames.runes_dl_01: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
            LocationNames.runes_id_01: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
            LocationNames.runes_id_02: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
            LocationNames.runes_dw_01: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
            LocationNames.runes_dw_02: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
            LocationNames.runes_bf_01: lambda player: lambda state: state.has(ItemNames.l_tower_key, player) and \
                state.has(ItemNames.yr_1, player) and \
                state.has(ItemNames.yr_2, player) and \
                state.has(ItemNames.yr_3, player) and \
                state.has(ItemNames.gn_1, player) and \
                state.has(ItemNames.gn_2, player) and \
                state.has(ItemNames.gn_3, player) and \
                state.has(ItemNames.bl_1, player) and \
                state.has(ItemNames.bl_2, player) and \
                state.has(ItemNames.bl_3, player) and \
                state.has(ItemNames.rd_1, player) and \
                state.has(ItemNames.rd_2, player) and \
                state.has(ItemNames.rd_3, player) and \
                state.has(ItemNames.bf_13, player),
        },
            ItemNames.shard: {
            LocationNames.boss_fp: lambda player: lambda state: state.has(ItemNames.lw_fp,player),
            LocationNames.boss_cs: lambda player: lambda state:
                state.has(ItemNames.w_wing_key, player),
            LocationNames.boss_sd: lambda player: lambda state:
                state.has(ItemNames.w_wing_key, player),
            LocationNames.boss_fr: lambda player: lambda state:
                state.has(ItemNames.w_wing_key, player),
            LocationNames.boss_dl: lambda player: lambda state:
                state.has(ItemNames.e_wing_key, player),
            LocationNames.boss_id: lambda player: lambda state:
                state.has(ItemNames.e_wing_key, player),
            LocationNames.boss_dw: lambda player: lambda state:
                state.has(ItemNames.e_wing_key, player),

            LocationNames.boss_dt: lambda player: lambda state:
                state.has(ItemNames.shard_fp, player) and \
                state.has(ItemNames.shard_mk, player) and \
                state.has(ItemNames.shard_cs, player) and \
                state.has(ItemNames.shard_sd, player) and \
                state.has(ItemNames.shard_fr, player) and \
                state.has(ItemNames.shard_dl, player) and \
                state.has(ItemNames.shard_id, player) and \
                state.has(ItemNames.shard_dw, player),
            LocationNames.boss_uw: lambda player: lambda state: state.has(ItemNames.yr_1, player) and \
                state.has(ItemNames.yr_2, player) and \
                state.has(ItemNames.yr_3, player) and \
                state.has(ItemNames.gn_1, player) and \
                state.has(ItemNames.gn_2, player) and \
                state.has(ItemNames.gn_3, player) and \
                state.has(ItemNames.bl_1, player) and \
                state.has(ItemNames.bl_2, player) and \
                state.has(ItemNames.bl_3, player) and \
                state.has(ItemNames.rd_1, player) and \
                state.has(ItemNames.rd_2, player) and \
                state.has(ItemNames.rd_3, player),
            #rk rules
        },
    
            ItemNames.lw: {
            #rk rules
            LocationNames.lw_loc_cs: lambda player: lambda state: 
                state.has(ItemNames.w_wing_key, player),
            LocationNames.lw_loc_sd: lambda player: lambda state: 
                state.has(ItemNames.w_wing_key, player),
            LocationNames.lw_loc_fr: lambda player: lambda state: 
                state.has(ItemNames.w_wing_key, player),
            LocationNames.lw_loc_dl: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
            LocationNames.lw_loc_id: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
            LocationNames.lw_loc_dw: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
            LocationNames.lw_loc_dt: lambda player: lambda state: state.has(ItemNames.shard_fp, player) and \
                state.has(ItemNames.shard_mk, player) and \
                state.has(ItemNames.shard_cs, player) and \
                state.has(ItemNames.shard_sd, player) and \
                state.has(ItemNames.shard_fr, player) and \
                state.has(ItemNames.shard_dl, player) and \
                state.has(ItemNames.shard_id, player) and \
                state.has(ItemNames.shard_dw, player),
        },
            ItemNames.region_key: {
            #region key rules
            LocationNames.tr_cs: lambda player: lambda state: 
                state.has(ItemNames.w_wing_key, player),
            LocationNames.tr_sd: lambda player: lambda state: 
                state.has(ItemNames.w_wing_key, player),
            LocationNames.tr_fr: lambda player: lambda state: 
                state.has(ItemNames.w_wing_key, player),
            LocationNames.tr_dl: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
            LocationNames.tr_id: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
            LocationNames.tr_dw: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
            LocationNames.tr_bf: lambda player: lambda state: state.has(ItemNames.l_tower_key, player) and \
                state.has(ItemNames.yr_1, player) and \
                state.has(ItemNames.yr_2, player) and \
                state.has(ItemNames.yr_3, player) and \
                state.has(ItemNames.gn_1, player) and \
                state.has(ItemNames.gn_2, player) and \
                state.has(ItemNames.gn_3, player) and \
                state.has(ItemNames.bl_1, player) and \
                state.has(ItemNames.bl_2, player) and \
                state.has(ItemNames.bl_3, player) and \
                state.has(ItemNames.rd_1, player) and \
                state.has(ItemNames.rd_2, player) and \
                state.has(ItemNames.rd_3, player) and \
                state.has(ItemNames.bf_13, player),
            LocationNames.rk_sd: lambda player: lambda state: state.has(ItemNames.w_wing_key, player),
            LocationNames.rk_fr: lambda player: lambda state: state.has(ItemNames.w_wing_key, player),
            LocationNames.rk_dl: lambda player: lambda state: state.has(ItemNames.w_wing_key, player),
            LocationNames.rk_id: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
            LocationNames.rk_dw: lambda player: lambda state: state.has(ItemNames.e_wing_key, player),
        }
        }
]

region_key_rules = [
    # connections. How do I mark X number of regions for a wing? make an item names class?

    # locations
    #not in use for now. Will add later
    {        ConnectionNames.lower_uw00: lambda player: lambda state: state.has(ItemNames.yr_1, player) and \
                state.has(ItemNames.yr_2, player) and \
                state.has(ItemNames.yr_3, player) and \
                state.has(ItemNames.gn_1, player) and \
                state.has(ItemNames.gn_2, player) and \
                state.has(ItemNames.gn_3, player) and \
                state.has(ItemNames.bl_1, player) and \
                state.has(ItemNames.bl_2, player) and \
                state.has(ItemNames.bl_3, player) and \
                state.has(ItemNames.rd_1, player) and \
                state.has(ItemNames.rd_2, player) and \
                state.has(ItemNames.rd_3, player),
        ConnectionNames.bf00_bf04: lambda player: lambda state: state.has(ItemNames.yr_1, player) and \
                state.has(ItemNames.yr_2, player) and \
                state.has(ItemNames.yr_3, player) and \
                state.has(ItemNames.gn_1, player) and \
                state.has(ItemNames.gn_2, player) and \
                state.has(ItemNames.gn_3, player) and \
                state.has(ItemNames.bl_1, player) and \
                state.has(ItemNames.bl_2, player) and \
                state.has(ItemNames.bl_3, player) and \
                state.has(ItemNames.rd_1, player) and \
                state.has(ItemNames.rd_2, player) and \
                state.has(ItemNames.rd_3, player) and \
                state.has(ItemNames.region_key_bf, player) and \
                state.has(ItemNames.bf_13, player),
        ConnectionNames.hub1_dt: lambda player: lambda state: state.has(ItemNames.shard_fp, player) and \
                state.has(ItemNames.shard_mk, player) and \
                state.has(ItemNames.shard_cs, player) and \
                state.has(ItemNames.shard_sd, player) and \
                state.has(ItemNames.shard_fr, player) and \
                state.has(ItemNames.shard_dl, player) and \
                state.has(ItemNames.shard_id, player) and \
                state.has(ItemNames.shard_dw, player),
    
        ConnectionNames.hub1_west: lambda player: lambda state: state.has(ItemNames.w_wing_key, player),
        ConnectionNames.hub1_east: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
        ConnectionNames.hub1_lower: lambda player: lambda state: state.has(ItemNames.l_tower_key, player),
    
    #region key rules

        ConnectionNames.hub1_mk: lambda player: lambda state: state.has(ItemNames.region_key_mk, player),
        ConnectionNames.west_cs00: lambda player: lambda state: state.has(ItemNames.region_key_cs, player),
        ConnectionNames.west_sd00: lambda player: lambda state: state.has(ItemNames.region_key_sd, player),
        ConnectionNames.west_fr00: lambda player: lambda state: state.has(ItemNames.region_key_fr, player),
        ConnectionNames.east_dl00: lambda player: lambda state: state.has(ItemNames.region_key_dl, player),
        ConnectionNames.east_id00: lambda player: lambda state: state.has(ItemNames.region_key_id, player),
        ConnectionNames.east_dw00: lambda player: lambda state: state.has(ItemNames.region_key_dw, player),
        ConnectionNames.lower_bf00: lambda player: lambda state: state.has(ItemNames.region_key_bf, player)
        
    },
    # locations
    {ItemNames.runes: {
            LocationNames.runes_mk_01: lambda player: lambda state: state.has(ItemNames.region_key_mk, player),
            LocationNames.runes_cs_01: lambda player: lambda state: state.has(ItemNames.w_wing_key, player) and \
                state.has(ItemNames.region_key_cs, player),
            LocationNames.runes_sd_01: lambda player: lambda state: state.has(ItemNames.w_wing_key, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.runes_sd_02: lambda player: lambda state: state.has(ItemNames.w_wing_key, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.runes_fr_01: lambda player: lambda state: state.has(ItemNames.w_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player),
            LocationNames.runes_dl_01: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.runes_id_01: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.runes_id_02: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.runes_dw_01: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.runes_dw_02: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.runes_bf_01: lambda player: lambda state: state.has(ItemNames.l_tower_key, player) and \
                state.has(ItemNames.yr_1, player) and \
                state.has(ItemNames.yr_2, player) and \
                state.has(ItemNames.yr_3, player) and \
                state.has(ItemNames.gn_1, player) and \
                state.has(ItemNames.gn_2, player) and \
                state.has(ItemNames.gn_3, player) and \
                state.has(ItemNames.bl_1, player) and \
                state.has(ItemNames.bl_2, player) and \
                state.has(ItemNames.bl_3, player) and \
                state.has(ItemNames.rd_1, player) and \
                state.has(ItemNames.rd_2, player) and \
                state.has(ItemNames.rd_3, player) and \
                state.has(ItemNames.region_key_bf, player) and \
                state.has(ItemNames.bf_13, player),
        },
            ItemNames.shard: {
            LocationNames.boss_fp: lambda player: lambda state: state.has(ItemNames.lw_fp,player),
            LocationNames.boss_mk: lambda player: lambda state: 
                state.has(ItemNames.region_key_mk, player),
            LocationNames.boss_cs: lambda player: lambda state:
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.w_wing_key, player),
            LocationNames.boss_sd: lambda player: lambda state:
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.w_wing_key, player),
            LocationNames.boss_fr: lambda player: lambda state:
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.w_wing_key, player),
            LocationNames.boss_dl: lambda player: lambda state:
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.boss_id: lambda player: lambda state:
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.boss_dw: lambda player: lambda state:
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.boss_dt: lambda player: lambda state:
                state.has(ItemNames.shard_fp, player) and \
                state.has(ItemNames.shard_mk, player) and \
                state.has(ItemNames.shard_cs, player) and \
                state.has(ItemNames.shard_sd, player) and \
                state.has(ItemNames.shard_fr, player) and \
                state.has(ItemNames.shard_dl, player) and \
                state.has(ItemNames.shard_id, player) and \
                state.has(ItemNames.shard_dw, player),
            LocationNames.boss_uw: lambda player: lambda state: state.has(ItemNames.yr_1, player) and \
                state.has(ItemNames.yr_2, player) and \
                state.has(ItemNames.yr_3, player) and \
                state.has(ItemNames.gn_1, player) and \
                state.has(ItemNames.gn_2, player) and \
                state.has(ItemNames.gn_3, player) and \
                state.has(ItemNames.bl_1, player) and \
                state.has(ItemNames.bl_2, player) and \
                state.has(ItemNames.bl_3, player) and \
                state.has(ItemNames.rd_1, player) and \
                state.has(ItemNames.rd_2, player) and \
                state.has(ItemNames.rd_3, player),
            #rk rules
        },
    
            ItemNames.lw: {
            #rk rules
            LocationNames.lw_loc_mk: lambda player: lambda state: state.has(ItemNames.region_key_mk, player),
            LocationNames.lw_loc_cs: lambda player: lambda state: state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.w_wing_key, player),
            LocationNames.lw_loc_sd: lambda player: lambda state: state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.w_wing_key, player),
            LocationNames.lw_loc_fr: lambda player: lambda state: state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.w_wing_key, player),
            LocationNames.lw_loc_dl: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.lw_loc_id: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.lw_loc_dw: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.lw_loc_dt: lambda player: lambda state: state.has(ItemNames.shard_fp, player) and \
                state.has(ItemNames.shard_mk, player) and \
                state.has(ItemNames.shard_cs, player) and \
                state.has(ItemNames.shard_sd, player) and \
                state.has(ItemNames.shard_fr, player) and \
                state.has(ItemNames.shard_dl, player) and \
                state.has(ItemNames.shard_id, player) and \
                state.has(ItemNames.shard_dw, player),
        },
            ItemNames.region_key: {
            #region key rules
            LocationNames.tr_mk: lambda player: lambda state: state.has(ItemNames.region_key_mk, player),
            LocationNames.tr_cs: lambda player: lambda state: state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.w_wing_key, player),
            LocationNames.tr_sd: lambda player: lambda state: state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.w_wing_key, player),
            LocationNames.tr_fr: lambda player: lambda state: state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.w_wing_key, player),
            LocationNames.tr_dl: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.tr_id: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.tr_dw: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dw, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.tr_bf: lambda player: lambda state: state.has(ItemNames.l_tower_key, player) and \
                state.has(ItemNames.yr_1, player) and \
                state.has(ItemNames.yr_2, player) and \
                state.has(ItemNames.yr_3, player) and \
                state.has(ItemNames.gn_1, player) and \
                state.has(ItemNames.gn_2, player) and \
                state.has(ItemNames.gn_3, player) and \
                state.has(ItemNames.bl_1, player) and \
                state.has(ItemNames.bl_2, player) and \
                state.has(ItemNames.bl_3, player) and \
                state.has(ItemNames.rd_1, player) and \
                state.has(ItemNames.rd_2, player) and \
                state.has(ItemNames.rd_3, player) and \
                state.has(ItemNames.region_key_bf, player) and \
                state.has(ItemNames.bf_13, player),
            LocationNames.rk_cs: lambda player: lambda state:
                state.has(ItemNames.region_key_mk, player),
            LocationNames.rk_sd: lambda player: lambda state: state.has(ItemNames.w_wing_key, player) and \
                state.has(ItemNames.region_key_cs, player),
            LocationNames.rk_fr: lambda player: lambda state: state.has(ItemNames.w_wing_key, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.rk_dl: lambda player: lambda state: state.has(ItemNames.w_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player),
            LocationNames.rk_id: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_dl, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player),
            LocationNames.rk_dw: lambda player: lambda state: state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_mk, player) and \
                state.has(ItemNames.region_key_sd, player) and \
                state.has(ItemNames.region_key_fr, player) or 
                state.has(ItemNames.region_key_id, player) and \
                state.has(ItemNames.e_wing_key, player) and \
                state.has(ItemNames.region_key_fr, player) and \
                state.has(ItemNames.region_key_cs, player) and \
                state.has(ItemNames.region_key_sd, player), 
            },
        


        }

    
]



def _add_rules(world: MultiWorld, player: int, rules: List, allowed_loc_types: List[str]):
    for name, rule_factory in rules[0].items():
        if type(rule_factory) == tuple and len(rule_factory) > 1 and rule_factory[1]:  # force override
            rule_factory = rule_factory[0]
            set_rule(world.get_entrance(name, player), rule_factory(player))
        else:
            add_rule(world.get_entrance(name, player), rule_factory(player))
    for loc_type, type_rules in rules[1].items():
        if loc_type not in allowed_loc_types:
            continue
        for name, rule_factory in type_rules.items():
            if type(rule_factory) == tuple and len(rule_factory) > 1 and rule_factory[1]:  # force override
                rule_factory = rule_factory[0]
                set_rule(world.get_location(name, player), rule_factory(player))
            else:
                add_rule(world.get_location(name, player), rule_factory(player))

def _set_rules(world: MultiWorld, player: int, rules: List, allowed_loc_types: List[str]):
    for name, rule_factory in rules[0].items():
        set_rule(world.get_entrance(name, player), rule_factory(player))
    for loc_type, type_rules in rules[1].items():
        if loc_type not in allowed_loc_types:
            continue
        for name, rule_factory in type_rules.items():
            set_rule(world.get_location(name, player), rule_factory(player))


def set_rules(world: MultiWorld, options: GDLOptions, player: int):
    allowed_loc_types = [ItemNames.runes,ItemNames.shard,ItemNames.lw,ItemNames.wing_key,ItemNames.region_key]

    _add_rules(world, player, base_rules, allowed_loc_types)
    if options.randomize_world_order.value:
        _set_rules(world, player, region_key_rules, allowed_loc_types)
        
    world.completion_condition[player] = lambda state: state.has("Victory", player)
