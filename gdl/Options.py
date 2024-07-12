from dataclasses import dataclass

from Options import Toggle, DeathLink, Range, Choice, PerGameCommonOptions

class RandomizeWorldOrder(Toggle):
    """If enabled, world order will be randomized and worlds will be locked behind region keys. If disabled, world order will remain the same and worlds will be unlocked when you gather the necessary crystals"""
    display_name = "Randomize World Order"
    default = 0

@dataclass
class GDLOptions(PerGameCommonOptions):
    randomize_world_order:RandomizeWorldOrder
    death_link: DeathLink
