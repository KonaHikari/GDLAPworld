from dataclasses import dataclass

from Options import Toggle, DeathLink, Range, Choice, PerGameCommonOptions


@dataclass
class GDLOptions(PerGameCommonOptions):

    death_link: DeathLink
