from typing import List, Dict

from . import GDLOptions
from .Locations import GDLLocation, location_table, \
    runes_location_table, boss_location_table, legendary_weapons_location_table, treasure_rooms_location_table, region_key_location_table
from .names import ConnectionNames, LevelNames, RegionNames, LocationNames

from BaseClasses import MultiWorld, Region, Entrance


def create_region(world: MultiWorld, player: int, name: str, locations=None, exits=None) -> Region:
    ret = Region(name, player, world)
    if locations:
        for location in locations:
            loc_id = location_table[location]
            location = GDLLocation(player, location, loc_id, ret)
            ret.locations.append(location)
    if exits:
        for _exit in exits:
            ret.exits.append(Entrance(player, _exit, ret))
    return ret


def _get_locations_for_region(locations: GDLLocation, name: str) -> List[str]:
    result = [k for k in location_table if f"{name}:" in k]
    if name == RegionNames.bf04:
        result += [LocationNames.credits]
    return result


exit_table: Dict[str, List[str]] = {
    RegionNames.menu: [ConnectionNames.start_game],
    RegionNames.hub1: [ConnectionNames.hub1_fp,ConnectionNames.hub1_mk,ConnectionNames.hub1_west,ConnectionNames.hub1_east,ConnectionNames.hub1_lower, ConnectionNames.hub1_dt],
    RegionNames.west: [ConnectionNames.west_hub1, ConnectionNames.west_cs00, ConnectionNames.west_fr00,
                       ConnectionNames.west_sd00],
    RegionNames.east: [ConnectionNames.east_hub1, ConnectionNames.east_dl00, ConnectionNames.east_id00,
                       ConnectionNames.east_dw00],
    RegionNames.lower: [ConnectionNames.lower_hub1,ConnectionNames.lower_uw00,ConnectionNames.lower_bf00],
    RegionNames.fp00: [ConnectionNames.fp00_fp01, ConnectionNames.fp00_fp02, ConnectionNames.fp00_fp03, ConnectionNames.fp00_fp04, ConnectionNames.fp00_fp05, ConnectionNames.fp_hub1],
    RegionNames.fp01: [ConnectionNames.fp01_fp00],
    RegionNames.fp02: [ConnectionNames.fp02_fp00],
    RegionNames.fp03: [ConnectionNames.fp03_fp00],
    RegionNames.fp04: [ConnectionNames.fp04_fp00],
    RegionNames.fp05: [ConnectionNames.fp05_fp00],
    RegionNames.mk00: [ConnectionNames.mk00_mk01, ConnectionNames.mk00_mk02, ConnectionNames.mk00_mk03, ConnectionNames.mk00_mk04, ConnectionNames.mk00_mk05, ConnectionNames.mk00_mk06, ConnectionNames.mk_hub1],
    RegionNames.mk01: [ConnectionNames.mk01_mk00],
    RegionNames.mk02: [ConnectionNames.mk02_mk00],
    RegionNames.mk03: [ConnectionNames.mk03_mk00],
    RegionNames.mk04: [ConnectionNames.mk04_mk00],
    RegionNames.mk05: [ConnectionNames.mk05_mk00],
    RegionNames.mk06: [ConnectionNames.mk05_mk00],
    RegionNames.cs00: [ConnectionNames.cs00_cs01, ConnectionNames.cs00_cs02, ConnectionNames.cs00_cs03, ConnectionNames.cs00_cs04, ConnectionNames.cs00_cs05, ConnectionNames.cs00_cs06, ConnectionNames.cs00_west],
    RegionNames.cs01: [ConnectionNames.cs01_cs00],
    RegionNames.cs02: [ConnectionNames.cs02_cs00],
    RegionNames.cs03: [ConnectionNames.cs03_cs00],
    RegionNames.cs04: [ConnectionNames.cs04_cs00],
    RegionNames.cs05: [ConnectionNames.cs05_cs00],
    RegionNames.cs06: [ConnectionNames.cs06_cs00],
    RegionNames.sd00: [ConnectionNames.sd00_sd01, ConnectionNames.sd00_sd02, ConnectionNames.sd00_sd03, ConnectionNames.sd00_sd04, ConnectionNames.sd00_sd05, ConnectionNames.sd00_west],
    RegionNames.sd01: [ConnectionNames.sd01_sd00],
    RegionNames.sd02: [ConnectionNames.sd02_sd00],
    RegionNames.sd03: [ConnectionNames.sd03_sd00],
    RegionNames.sd04: [ConnectionNames.sd04_sd00],
    RegionNames.sd05: [ConnectionNames.sd05_sd00],
    RegionNames.fr00: [ConnectionNames.fr00_fr01, ConnectionNames.fr00_fr02, ConnectionNames.fr00_fr03, ConnectionNames.fr00_fr04, ConnectionNames.fr00_fr05, ConnectionNames.fr00_west],
    RegionNames.fr01: [ConnectionNames.fr01_fr00],
    RegionNames.fr02: [ConnectionNames.fr02_fr00],
    RegionNames.fr03: [ConnectionNames.fr03_fr00],
    RegionNames.fr04: [ConnectionNames.fr04_fr00],
    RegionNames.fr05: [ConnectionNames.fr05_fr00],
    RegionNames.dl00: [ConnectionNames.dl00_dl01, ConnectionNames.dl00_dl02, ConnectionNames.dl00_dl03, ConnectionNames.dl00_dl04, ConnectionNames.dl00_dl05, ConnectionNames.dl00_east],
    RegionNames.dl01: [ConnectionNames.dl01_dl00],
    RegionNames.dl02: [ConnectionNames.dl02_dl00],
    RegionNames.dl03: [ConnectionNames.dl03_dl00],
    RegionNames.dl04: [ConnectionNames.dl04_dl00],
    RegionNames.dl05: [ConnectionNames.dl05_dl00],
    RegionNames.id00: [ConnectionNames.id00_id01, ConnectionNames.id00_id02, ConnectionNames.id00_id03, ConnectionNames.id00_id04, ConnectionNames.id00_id05, ConnectionNames.id00_east],
    RegionNames.id01: [ConnectionNames.id01_id00],
    RegionNames.id02: [ConnectionNames.id02_id00],
    RegionNames.id03: [ConnectionNames.id03_id00],
    RegionNames.id04: [ConnectionNames.id04_id00],
    RegionNames.id05: [ConnectionNames.id05_id00],
    RegionNames.dw00: [ConnectionNames.dw00_dw01, ConnectionNames.dw00_dw02, ConnectionNames.dw00_dw03, ConnectionNames.dw00_dw04, ConnectionNames.dw00_dw05, ConnectionNames.dw00_dw06, ConnectionNames.dw00_east],
    RegionNames.dw01: [ConnectionNames.dw01_dw00],
    RegionNames.dw02: [ConnectionNames.dw02_dw00],
    RegionNames.dw03: [ConnectionNames.dw03_dw00],
    RegionNames.dw04: [ConnectionNames.dw04_dw00],
    RegionNames.dw05: [ConnectionNames.dw05_dw00],
    RegionNames.dw06: [ConnectionNames.dw06_dw00],
    RegionNames.bf00: [ConnectionNames.bf00_bf01, ConnectionNames.bf00_bf02, ConnectionNames.bf00_bf03, ConnectionNames.bf00_bf04, ConnectionNames.bf00_lower],
    RegionNames.bf01: [ConnectionNames.bf01_bf00],
    RegionNames.bf02: [ConnectionNames.bf02_bf00],
    RegionNames.bf03: [ConnectionNames.bf03_bf00],
    RegionNames.bf04: [ConnectionNames.bf04_bf00],
    RegionNames.dt00: [ConnectionNames.dt_hub1],
    RegionNames.uw00: [ConnectionNames.uw00_lower],
}


def create_regions(world: MultiWorld, options: GDLOptions, player: int):
    # create regions
    world.regions += [
        create_region(world, player, k, _get_locations_for_region(options, k), v) for k, v in exit_table.items()
    ]

    # connect regions
    world.get_entrance(ConnectionNames.start_game, player).connect(world.get_region(RegionNames.hub1, player))
    for k, v in exit_table.items():
        if k == RegionNames.menu:
            continue
        for _exit in v:
            exit_regions = _exit.split('->')
            assert len(exit_regions) == 2
            # ToDo: warp rando
            target = world.get_region(exit_regions[1], player)
            world.get_entrance(_exit, player).connect(target)
