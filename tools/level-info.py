#!/usr/bin/env python3
"""檢查 Minecraft 世界資料夾：版本、模式、資料夾結構，以及搬到 Fabric 26.3 要做什麼。

用法:
    python3 tools/level-info.py /path/to/world

只讀取檔案，不會修改世界。只使用標準函式庫。
"""
from __future__ import annotations

import gzip
import struct
import sys
from pathlib import Path

TARGET_NAME = "26.3"
TARGET_DATA_VERSION = 5023  # 26.3 的 DataVersion
GAME_TYPES = {0: "survival", 1: "creative", 2: "adventure", 3: "spectator"}


class NBT:
    def __init__(self, data: bytes) -> None:
        self.d, self.p = data, 0

    def take(self, n: int) -> bytes:
        b = self.d[self.p:self.p + n]
        self.p += n
        return b

    def string(self) -> str:
        return self.take(struct.unpack(">H", self.take(2))[0]).decode("utf-8", "replace")

    def payload(self, t: int):
        if t == 1: return self.take(1)[0]
        if t == 2: return struct.unpack(">h", self.take(2))[0]
        if t == 3: return struct.unpack(">i", self.take(4))[0]
        if t == 4: return struct.unpack(">q", self.take(8))[0]
        if t == 5: return struct.unpack(">f", self.take(4))[0]
        if t == 6: return struct.unpack(">d", self.take(8))[0]
        if t == 7: self.take(self.payload(3)); return None
        if t == 8: return self.string()
        if t == 9:
            et, n = self.take(1)[0], self.payload(3)
            return [self.payload(et) for _ in range(n)]
        if t == 10:
            out = {}
            while (tt := self.take(1)[0]) != 0:
                k = self.string()
                out[k] = self.payload(tt)
            return out
        if t == 11: self.take(4 * self.payload(3)); return None
        if t == 12: self.take(8 * self.payload(3)); return None
        raise ValueError(f"unknown NBT tag {t}")

    def root(self) -> dict:
        self.take(1); self.string()
        return self.payload(10)


def count_mca(d: Path) -> int:
    return len(list(d.glob("*.mca"))) if d.is_dir() else 0


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    world = Path(sys.argv[1]).resolve()
    level = world / "level.dat"
    if not level.is_file():
        sys.exit(f"{level} 不存在：請指定含有 level.dat 的世界資料夾")

    data = NBT(gzip.open(level).read()).root()["Data"]
    ver = data.get("Version", {})
    name, dv = ver.get("Name", "?(1.9 以前)"), data.get("DataVersion", ver.get("Id", 0))
    print(f"世界資料夾 : {world}")
    print(f"存檔版本   : {name}(DataVersion {dv})")
    print(f"預設模式   : {GAME_TYPES.get(data.get('GameType'), data.get('GameType'))}"
          f"{'、極限' if data.get('hardcore') else ''}")
    print(f"世界名稱   : {data.get('LevelName')}")

    # 資料夾結構
    dims = world / "dimensions" / "minecraft"
    siblings = {"nether": world.parent / f"{world.name}_nether", "end": world.parent / f"{world.name}_the_end"}
    if dims.is_dir():
        layout = "26.x 新結構(world/dimensions/...)"
        regions = {d: count_mca(dims / d / "region") for d in ("overworld", "the_nether", "the_end")}
    else:
        regions = {"overworld": count_mca(world / "region"),
                   "the_nether": count_mca(world / "DIM-1" / "region"),
                   "the_end": count_mca(world / "DIM1" / "region")}
        if regions["the_nether"] or regions["the_end"]:
            layout = "原版舊結構(地獄、終界在 world/DIM-1、world/DIM1)"
        elif siblings["nether"].is_dir() or siblings["end"].is_dir():
            layout = "Paper/Spigot 分開結構(地獄、終界在 world_nether/、world_the_end/)"
            regions["the_nether"] = count_mca(siblings["nether"] / "DIM-1" / "region")
            regions["the_end"] = count_mca(siblings["end"] / "DIM1" / "region")
        else:
            layout = "原版舊結構(只找到主世界)"
    print(f"資料夾結構 : {layout}")
    print("region 檔數: " + "、".join(f"{k} {v}" for k, v in regions.items()))

    print("\n搬到 TechSMP(Fabric 26.3)需要:")
    if dv == TARGET_DATA_VERSION:
        print("  - 版本相同，不需要升級")
    elif dv > TARGET_DATA_VERSION:
        print(f"  - ⚠ 存檔版本 {name} 比 26.3 新:Minecraft 不能降版，不要直接開服，先跟管理者確認")
    else:
        print(f"  - 第一次啟動會把 {name} 升級成 26.3,**不可逆**,開服前務必完整備份原始世界")
    if "Paper/Spigot" in layout:
        print(f"  - 先把 {siblings['nether'].name}/DIM-1 搬到 {world.name}/DIM-1、"
              f"{siblings['end'].name}/DIM1 搬到 {world.name}/DIM1,再放進 techsmp/data/world")
        print("  - Paper 插件的資料(Essentials 的 home、CoreProtect 紀錄等)不會帶過去")
    else:
        print("  - 整個資料夾直接放成 techsmp/data/world 即可")
    if not dims.is_dir():
        print("  - 第一次啟動時伺服器會自動改成 26.x 的 dimensions/ 結構(log 會出現 World storage migration)")


if __name__ == "__main__":
    main()
