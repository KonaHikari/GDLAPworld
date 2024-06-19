import hashlib
import json
import logging
import os
import sys
import tempfile
import zipfile
from enum import Enum
from typing import Any

import Utils
from worlds.Files import AutoPatchRegister, APContainer
from . import Patches
from .inc.wwrando.wwlib.gcm import GCM


GDL_HASH = "308cab2e7a82f72a5aed2209d766f65a"

class GDLDeltaPatch(APContainer, metaclass=AutoPatchRegister):
    hash = GDL_HASH
    game = "Gauntlet Dark Legacy"
    patch_file_ending: str = ".apgdl"
    result_file_ending: str = ".gcm"
    zip_version: int = 1
    logger = logging.getLogger("gdlPatch")

    def __init__(self, *args: Any, **kwargs: Any):
        self.seed: bytes = kwargs['seed']
        del kwargs['seed']
        super(GDLDeltaPatch, self).__init__(*args, **kwargs)

    def write_contents(self, opened_zipfile: zipfile.ZipFile):
        super(GDLDeltaPatch, self).write_contents(opened_zipfile)
        opened_zipfile.writestr("zip_version",
                                self.zip_version.to_bytes(1, "little"),
                                compress_type=zipfile.ZIP_STORED)
        m = hashlib.md5()
        m.update(self.seed)
        opened_zipfile.writestr("seed",
                                m.digest(),
                                compress_type=zipfile.ZIP_STORED)

    def read_contents(self, opened_zipfile: zipfile.ZipFile) -> None:
        super(GDLDeltaPatch, self).read_contents(opened_zipfile)

    @classmethod
    def get_int(cls, opened_zipfile: zipfile.ZipFile, name: str):
        if name not in opened_zipfile.namelist():
            cls.logger.warning(f"couldn't find {name} in patch file")
            return 0
        return int.from_bytes(opened_zipfile.read(name), "little")

    @classmethod
    def get_bool(cls, opened_zipfile: zipfile.ZipFile, name: str):
        if name not in opened_zipfile.namelist():
            cls.logger.warning(f"couldn't find {name} in patch file")
            return False
        return bool.from_bytes(opened_zipfile.read(name), "little")

    @classmethod
    def get_json_obj(cls, opened_zipfile: zipfile.ZipFile, name: str):
        if name not in opened_zipfile.namelist():
            cls.logger.warning(f"couldn't find {name} in patch file")
            return None
        with opened_zipfile.open(name, "r") as f:
            obj = json.load(f)
        return obj

    @classmethod
    def get_seed_hash(cls, opened_zipfile: zipfile.ZipFile):
        return opened_zipfile.read("seed")


    @classmethod
    async def apply_binary_changes(cls, opened_zipfile: zipfile.ZipFile, iso):
        cls.logger.info('--binary patching--')
        # get slot name and seed hash
        manifest = GDLDeltaPatch.get_json_obj(opened_zipfile, "archipelago.json")
        slot_name = manifest["player_name"]
        slot_name_bytes = slot_name.encode('utf-8')
        slot_name_offset = 0x2AB980
        seed_hash = GDLDeltaPatch.get_seed_hash(opened_zipfile)
        seed_hash_offset = slot_name_offset + 0x40
        # always apply these patches
        patches = [Patches.AP_SAVE_LOAD]
        # conditional patches


        with open(iso, "rb+") as stream:
            # write patches
            for patch in patches:
                cls.logger.info(f"applying patch {patches.index(patch) + 1}/{len(patches)}")
                for addr, val in patch.items():
                    stream.seek(addr, 0)
                    if isinstance(val, bytes):
                        stream.write(val)
                    else:
                        stream.write(val.to_bytes(0x4, "big"))
            # write slot name
            cls.logger.debug(f"writing slot_name {slot_name} to 0x{slot_name_offset:x} ({slot_name_bytes})")
            stream.seek(slot_name_offset, 0)
            stream.write(slot_name_bytes)
            cls.logger.debug(f"writing seed_hash {seed_hash} to 0x{seed_hash_offset:x}")
            stream.seek(seed_hash_offset, 0)
            stream.write(seed_hash)
        cls.logger.info('--binary patching done--')

    @classmethod
    def get_rom_path(cls) -> str:
        return get_base_rom_path()

    @classmethod
    def check_hash(cls):
        if not validate_hash():
            Exception(f"Supplied Base Rom does not match known MD5 for GDL (US). "
                      "Get the correct game and version.")

    @classmethod
    def check_version(cls, opened_zipfile: zipfile.ZipFile) -> bool:
        version_bytes = opened_zipfile.read("zip_version")
        version = 0
        if version_bytes is not None:
            version = int.from_bytes(version_bytes, "little")
        if version != cls.zip_version:
            return False
        return True


def get_base_rom_path(file_name: str = "") -> str:
    options: Utils.OptionsType = Utils.get_options()
    if not file_name:
        # file_name = options["gdl_options"]["rom_file"]
        file_name = "Gauntlet - Dark Legacy (USA)"
    if not os.path.exists(file_name):
        file_name = Utils.user_path(file_name)
    return file_name


def validate_hash(file_name: str = ""):
    file_name = get_base_rom_path(file_name)
    with open(file_name, "rb") as file:
        base_rom_bytes = bytes(file.read())
    basemd5 = hashlib.md5()
    basemd5.update(base_rom_bytes)
    return GDL_HASH == basemd5.hexdigest()
