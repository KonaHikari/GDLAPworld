import typing
from BaseClasses import Item, ItemClassification
from .names import ItemNames
from typing import List

cen_and_west: List[str] = [
    ItemNames.region_key_mk,
    ItemNames.region_key_cs,
    ItemNames.region_key_sd,
    ItemNames.region_key_fr]

class ItemData(typing.NamedTuple):
    id: typing.Optional[int]
    classification: ItemClassification

    def is_progression(self):
        return self.classification & ItemClassification.progression == ItemClassification.progression

    def is_trap(self):
        return self.classification & ItemClassification.trap == ItemClassification.trap

    def is_filler(self):
        return self.classification & ItemClassification.filler == ItemClassification.filler


class GDLItem(Item):
    game: str = "Gauntlet Dark Legacy"


base_id = 5240216

item_table = {
    # runestones
    ItemNames.yr_1: ItemData(base_id + 0, ItemClassification.progression),
    ItemNames.yr_2: ItemData(base_id + 1, ItemClassification.progression),
    ItemNames.yr_3: ItemData(base_id + 2, ItemClassification.progression),
    ItemNames.rd_1: ItemData(base_id + 3, ItemClassification.progression),
    ItemNames.rd_2: ItemData(base_id + 4, ItemClassification.progression),
    ItemNames.rd_3: ItemData(base_id + 5, ItemClassification.progression),
    ItemNames.bl_1: ItemData(base_id + 6, ItemClassification.progression),
    ItemNames.bl_2: ItemData(base_id + 7, ItemClassification.progression),
    ItemNames.bl_3: ItemData(base_id + 8, ItemClassification.progression),
    ItemNames.gn_1: ItemData(base_id + 9, ItemClassification.progression),
    ItemNames.gn_2: ItemData(base_id + 10, ItemClassification.progression),
    ItemNames.gn_3: ItemData(base_id + 11, ItemClassification.progression),
    ItemNames.bf_13: ItemData(base_id + 12, ItemClassification.progression),
    # shards
    ItemNames.shard_fp: ItemData(base_id + 13, ItemClassification.progression),
    ItemNames.shard_mk: ItemData(base_id + 14, ItemClassification.progression),
    ItemNames.shard_cs: ItemData(base_id + 15, ItemClassification.progression),
    ItemNames.shard_sd: ItemData(base_id + 16, ItemClassification.progression),
    ItemNames.shard_fr: ItemData(base_id + 17, ItemClassification.progression),
    ItemNames.shard_dl: ItemData(base_id + 18, ItemClassification.progression),
    ItemNames.shard_id: ItemData(base_id + 19, ItemClassification.progression),
    ItemNames.shard_dw: ItemData(base_id + 20, ItemClassification.progression),
    # legendary weapons
    ItemNames.lw_fp: ItemData(base_id + 25, ItemClassification.progression),
    ItemNames.lw_mk: ItemData(base_id + 21, ItemClassification.useful),
    ItemNames.lw_cs: ItemData(base_id + 22, ItemClassification.useful),
    ItemNames.lw_sd: ItemData(base_id + 23, ItemClassification.useful),
    ItemNames.lw_fr: ItemData(base_id + 24, ItemClassification.useful),
    ItemNames.lw_dl: ItemData(base_id + 26, ItemClassification.useful),
    ItemNames.lw_id: ItemData(base_id + 27, ItemClassification.useful),
    ItemNames.lw_dw: ItemData(base_id + 28, ItemClassification.useful),
    ItemNames.lw_dt: ItemData(base_id + 29, ItemClassification.useful),
    # region keys
    ItemNames.region_key_mk: ItemData(base_id + 30, ItemClassification.progression),
    ItemNames.region_key_cs: ItemData(base_id + 31, ItemClassification.progression),
    ItemNames.region_key_sd: ItemData(base_id + 32, ItemClassification.progression),
    ItemNames.region_key_fr: ItemData(base_id + 33, ItemClassification.progression),
    ItemNames.region_key_dl: ItemData(base_id + 34, ItemClassification.progression),
    ItemNames.region_key_id: ItemData(base_id + 35, ItemClassification.progression),
    ItemNames.region_key_dw: ItemData(base_id + 36, ItemClassification.progression),
    ItemNames.region_key_bf: ItemData(base_id + 37, ItemClassification.progression),
    # wing keys
    ItemNames.w_wing_key: ItemData(base_id + 38, ItemClassification.progression),
    ItemNames.e_wing_key: ItemData(base_id + 39, ItemClassification.progression),
    ItemNames.l_tower_key: ItemData(base_id + 40, ItemClassification.progression),
    # events
    ItemNames.victory: ItemData(None, ItemClassification.progression)
}

lookup_id_to_name: typing.Dict[int, str] = {data.id: name for name, data in item_table.items() if data.id}
