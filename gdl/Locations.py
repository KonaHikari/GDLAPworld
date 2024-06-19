import typing
from BaseClasses import Location
from .names import LocationNames


class GDLLocation(Location):
    game: str = "Gauntlet Dark Legacy"


base_id = 5240216

runes_location_table = {
    # FP (0-7)
    LocationNames.runes_fp_01: base_id + 0,
    LocationNames.runes_fp_02: base_id + 1,
    # MK (8-15)
    LocationNames.runes_mk_01: base_id + 8,
    # CR (16-23)
    LocationNames.runes_cs_01: base_id + 16,
    # SD (24-31)
    LocationNames.runes_sd_01: base_id + 24,
    LocationNames.runes_sd_02: base_id + 25,
    # FR (32)
    LocationNames.runes_fr_01: base_id + 32,
    # DL (33-40)
    LocationNames.runes_dl_01: base_id + 33,
    # ID (41-48)
    LocationNames.runes_id_01: base_id + 41,
    LocationNames.runes_id_02: base_id + 42,
    # DW (49-56)
    LocationNames.runes_dw_01: base_id + 49,
    LocationNames.runes_dw_02: base_id + 50,
    # BF (57)
    LocationNames.runes_bf_01: base_id + 57,
}

boss_location_table = {
    LocationNames.boss_fp: base_id + 100 + 0,
    LocationNames.boss_mk: base_id + 100 + 1,
    LocationNames.boss_cs: base_id + 100 + 2,
    LocationNames.boss_sd: base_id + 100 + 3,
    LocationNames.boss_fr: base_id + 100 + 4,
    LocationNames.boss_dl: base_id + 100 + 5,
    LocationNames.boss_id: base_id + 100 + 6,
    LocationNames.boss_dw: base_id + 100 + 7,
    LocationNames.boss_dt: base_id + 100 + 8,
    LocationNames.boss_uw: base_id + 100 + 9,
}

legendary_weapons_location_table = {
    LocationNames.lw_loc_fp: base_id + 183 + 0,
    LocationNames.lw_loc_mk: base_id + 183 + 1,
    LocationNames.lw_loc_cs: base_id + 183 + 2,
    LocationNames.lw_loc_sd: base_id + 183 + 3,
    LocationNames.lw_loc_fr: base_id + 183 + 4,
    LocationNames.lw_loc_dl: base_id + 183 + 5,
    LocationNames.lw_loc_id: base_id + 183 + 6,
    LocationNames.lw_loc_dw: base_id + 183 + 7,
    LocationNames.lw_loc_dt: base_id + 183 + 8,
}

treasure_rooms_location_table = {
    LocationNames.tr_fp: base_id + 210+1,
    LocationNames.tr_mk: base_id + 210+2,
    LocationNames.tr_cs: base_id + 210+3,
    LocationNames.tr_sd: base_id + 210+4,
    LocationNames.tr_fr: base_id + 210+5,
    LocationNames.tr_dl: base_id + 210+6,
    LocationNames.tr_id: base_id + 210+7,
    LocationNames.tr_dw: base_id + 210+8,
    LocationNames.tr_bf: base_id + 210+9,
}

location_table: typing.Dict[str, typing.Optional[int]] = {
    **runes_location_table,  # 0 - 99
    **boss_location_table,  # 100 - 179
    **legendary_weapons_location_table,  # 180 - 182
    **treasure_rooms_location_table,  # 183 - 233
    LocationNames.credits: None
}

lookup_id_to_name: typing.Dict[int, str] = {_id: name for name, _id in location_table.items()}
