import os
import typing
from multiprocessing import Process
from typing import TextIO
import Utils
from BaseClasses import Item, Tutorial, ItemClassification
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import Component, components, Type, SuffixIdentifier
from .Events import create_events
from .Items import item_table, GDLItem
from .Locations import location_table, GDLLocation
from .Options import GDLOptions
from .Regions import create_regions
from .Rom import GDLDeltaPatch
from .Rules import set_rules
from .names import ItemNames, ConnectionNames




    
def run_client():
    print('running gdl client')
    from worlds.gdl.GDLClient import main  # lazy import
    file_types = (('GDL Patch File', ('.apgdl',)), ('NGC iso', ('.gcm',)),)
    kwargs = {'patch_file': Utils.open_filename("Select .apgdl", file_types)}
    p = Process(target=main, kwargs=kwargs)
    p.start()


components.append(Component("GDL Client", func=run_client, component_type=Type.CLIENT,
                            file_identifier=SuffixIdentifier('.apgdl')))

#not needed? where is webworld?
class GauntletDarkLegacyWeb(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the The Binding Of Isaac Repentance integration for Archipelago multiworld games.",
        "English",
        "setup_en.md",
        "setup/en",
        ["KonaHikari"]
    )    ]



class GauntletDarkLegacy(World):
    """
Gauntlet Dark Legacy    ToDo
    """
    game = "Gauntlet Dark Legacy"
    options_dataclass = GDLOptions
    options: GDLOptions
    topology_present = False

    item_name_to_id = {name: data.id for name, data in item_table.items()}
    location_name_to_id = location_table


    web = GauntletDarkLegacyWeb()

    def get_filler_item_name(self) -> str:
        return ItemNames.nothing
    
    def get_items(self):
        filler_items = [ItemNames.nothing]
        filler_weights = [1]

        itempool = [ItemNames.yr_1,ItemNames.yr_2, ItemNames.yr_3, ItemNames.rd_1, ItemNames.rd_2, ItemNames.rd_3, ItemNames.bl_1, ItemNames.bl_2, ItemNames.bl_3, ItemNames.gn_1, ItemNames.gn_2, ItemNames.gn_3, ItemNames.bf_13,
                    ItemNames.shard_fp, ItemNames.shard_mk, ItemNames.shard_cs, ItemNames.shard_sd, ItemNames.shard_fr, ItemNames.shard_dl, ItemNames.shard_id, ItemNames.shard_dw,
                    ItemNames.lw_fp, ItemNames.lw_mk, ItemNames.lw_cs, ItemNames.lw_sd, ItemNames.lw_fr, ItemNames.lw_dl, ItemNames.lw_id, ItemNames.lw_dw, ItemNames.lw_dt,
                
                    ItemNames.e_wing_key, ItemNames.w_wing_key, ItemNames.l_tower_key]
        if self.options.randomize_world_order.value:
            itempool += [ItemNames.region_key_mk, ItemNames.region_key_cs, ItemNames.region_key_sd, ItemNames.region_key_fr, ItemNames.region_key_dl, ItemNames.region_key_id, ItemNames.region_key_dw, ItemNames.region_key_bf]
        k = 0
        for item in self.multiworld.precollected_items[self.player]:
            if item.name in itempool and item.advancement:
                itempool.remove(item.name)
                k = k + 1
        if k > 0:
            itempool += self.random.choices(filler_items, weights=filler_weights, k=k)
        # Convert itempool into real items
        itempool = list(map(lambda name: self.create_item(name), itempool))
        return itempool

    def create_items(self):
        self.multiworld.itempool += self.get_items()

    def set_rules(self):
        create_events(self.multiworld, self.player)
        set_rules(self.multiworld, self.options, self.player)

    def create_regions(self):
        create_regions(self.multiworld, self.options, self.player)

    def fill_slot_data(self):
        return {
            "death_link": self.options.death_link.value,
        }

    def create_item(self, name: str,) -> Item:
        item_data = item_table[name]
        classification = item_data.classification
        item = GDLItem(name, classification,
                        item_data.id, self.player)

        return item


    def generate_output(self, output_directory: str) -> None:
        patch = GDLDeltaPatch(path=os.path.join(output_directory,
                                                 f"{self.multiworld.get_out_file_name_base(self.player)}{GDLDeltaPatch.patch_file_ending}"),
                               player=self.player,
                               player_name=self.multiworld.get_player_name(self.player),
                               seed=self.multiworld.seed_name.encode('utf-8')
                                )
        patch.write()
