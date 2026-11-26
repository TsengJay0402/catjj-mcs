#!/usr/bin/env python3
"""把客戶端模組包(modrinth.index.json)轉成 CurseForge App 能匯入的 .zip。

用法:
    CURSEFORGE_API_KEY=... python3 tools/build-curseforge.py techsmp/client [--out dist]

先跑 tools/build-mrpack.py 產生最新的 modrinth.index.json。
API 金鑰從 https://console.curseforge.com/ 申請；CI 用 repo secret CURSEFORGE_API_KEY。

每個檔案怎麼放進 CurseForge 包:
    1. external-assets.json 註明「CurseForge project X, file Y」的 → 直接用這組 ID
    2. 其他的下載下來(核對 SHA-512)算 CurseForge 指紋，查 CurseForge 上有沒有一模一樣的檔案
       → 有就用該檔案的 project/file ID,由 CurseForge App 自己下載
    3. 查不到的，若 Modrinth 上標示的授權允許重新散佈(開源授權)→ 直接把檔案包進 overrides/
       不允許的：必裝 → 建置失敗；選用 → 略過並列在輸出的警告中
選用模組在 manifest 標 required=false(CurseForge App 會以停用狀態安裝，玩家自己在 App 裡打開)。

產物:dist/<name>-<version>-curseforge.zip(manifest.json + modlist.html + overrides/)
只使用標準函式庫。
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import struct
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

CF_API = "https://api.curseforge.com/v1"
MINECRAFT_GAME_ID = 432
MODRINTH_API = "https://api.modrinth.com/v2"
USER_AGENT = "catjj-mcs/build-curseforge (github.com/TsengJay0402/catjj-mcs)"
ZIP_TIMESTAMP = (2020, 1, 1, 0, 0, 0)
# 允許直接包進 overrides 的授權(SPDX ID)。All Rights Reserved 或自訂授權一律不包。
REDISTRIBUTABLE = re.compile(
    r"(MIT|Apache-2\.0|BSD-[0-9A-Za-z.-]+|0BSD|MPL-2\.0|(A|L)?GPL-[0-9.]+(-only|-or-later)?|CC0-1\.0|Unlicense|ISC|Zlib)"
)
CF_SOURCE = re.compile(r"CurseForge project (\d+), file (\d+)")


def request(url: str, data: bytes | None = None, headers: dict[str, str] | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def murmur2(data: bytes, seed: int = 1) -> int:
    m = 0x5BD1E995
    length = len(data)
    h = (seed ^ length) & 0xFFFFFFFF
    body = length - length % 4
    for (k,) in struct.iter_unpack("<I", data[:body]):
        k = (k * m) & 0xFFFFFFFF
        k ^= k >> 24
        k = (k * m) & 0xFFFFFFFF
        h = ((h * m) & 0xFFFFFFFF) ^ k
    tail = data[body:]
    if len(tail) >= 3:
        h ^= tail[2] << 16
    if len(tail) >= 2:
        h ^= tail[1] << 8
    if tail:
        h ^= tail[0]
        h = (h * m) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * m) & 0xFFFFFFFF
    h ^= h >> 15
    return h


def cf_fingerprint(data: bytes) -> int:
    # CurseForge 指紋：去掉 tab/換行/空白後的 MurmurHash2(seed 1)
    return murmur2(data.translate(None, b"\t\n\r "))


def fetch_file(f: dict, cache: Path) -> bytes:
    sha512 = f["hashes"]["sha512"]
    cached = cache / sha512
    if cached.exists():
        return cached.read_bytes()
    data = request(f["downloads"][0])
    if hashlib.sha512(data).hexdigest() != sha512:
        sys.exit(f"{f['path']}: 下載內容的 SHA-512 和 index 不符")
    cache.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(data)
    return data


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack_dir", type=Path)
    ap.add_argument("--out", type=Path, default=Path("dist"))
    args = ap.parse_args()

    key = os.environ.get("CURSEFORGE_API_KEY", "").strip()
    if not key:
        sys.exit("需要環境變數 CURSEFORGE_API_KEY(從 https://console.curseforge.com/ 申請)")

    pack = json.loads((args.pack_dir / "pack.json").read_text(encoding="utf-8"))
    index = json.loads((args.pack_dir / "modrinth.index.json").read_text(encoding="utf-8"))
    if index["versionId"] != pack["version"]:
        sys.exit("modrinth.index.json 不是最新的，先跑 tools/build-mrpack.py")
    external_path = args.pack_dir / "external-assets.json"
    external = json.loads(external_path.read_text(encoding="utf-8"))["files"] if external_path.exists() else []
    cf_ids = {a["path"]: CF_SOURCE.fullmatch(a["source"].strip()) for a in external}

    cache = args.out / ".cache"
    manifest_files: list[dict] = []
    listed: list[tuple[str, str]] = []  # (路徑, 說明) 給 modlist.html
    bundled: dict[str, bytes] = {}
    need_lookup: dict[int, tuple[dict, bytes]] = {}

    for f in index["files"]:
        required = f["env"]["client"] == "required"
        ids = cf_ids.get(f["path"])
        if ids:
            manifest_files.append({"projectID": int(ids[1]), "fileID": int(ids[2]), "required": required})
            listed.append((f["path"], f"CurseForge project {ids[1]}"))
            continue
        data = fetch_file(f, cache)
        need_lookup[cf_fingerprint(data)] = (f, data)

    matches: dict[int, dict] = {}
    if need_lookup:
        body = json.dumps({"fingerprints": sorted(need_lookup)}).encode()
        resp = json.loads(request(
            f"{CF_API}/fingerprints/{MINECRAFT_GAME_ID}", data=body,
            headers={"x-api-key": key, "Content-Type": "application/json", "Accept": "application/json"},
        ))
        for match in resp["data"]["exactMatches"]:
            matches[match["file"]["fileFingerprint"]] = match["file"]

    unmatched: list[dict] = []
    for fp, (f, data) in sorted(need_lookup.items(), key=lambda x: x[1][0]["path"]):
        required = f["env"]["client"] == "required"
        cf_file = matches.get(fp)
        if cf_file:
            manifest_files.append({"projectID": cf_file["modId"], "fileID": cf_file["id"], "required": required})
            listed.append((f["path"], f"CurseForge project {cf_file['modId']}"))
        else:
            unmatched.append(f)

    errors: list[str] = []
    warnings: list[str] = []
    if unmatched:
        project_of = {}
        for f in unmatched:
            m = re.match(r"https://cdn\.modrinth\.com/data/([A-Za-z0-9]+)/", f["downloads"][0])
            project_of[f["path"]] = m[1] if m else None
        ids = sorted({p for p in project_of.values() if p})
        projects = {}
        if ids:
            q = urllib.parse.urlencode({"ids": json.dumps(ids)})
            projects = {p["id"]: p for p in json.loads(request(f"{MODRINTH_API}/projects?{q}"))}
        for f in unmatched:
            p = projects.get(project_of[f["path"]])
            license_id = (p or {}).get("license", {}).get("id", "")
            name = p["title"] if p else f["path"]
            if REDISTRIBUTABLE.fullmatch(license_id):
                bundled[f"overrides/{f['path']}"] = fetch_file(f, cache)
                source = f"https://modrinth.com/project/{p['slug']}"
                listed.append((f["path"], f"CurseForge 上沒有相同檔案，依 {license_id} 授權直接附在包內(原始來源 {source})"))
            elif f["env"]["client"] == "required":
                errors.append(f"{name}({f['path']}):CurseForge 上找不到相同檔案，授權 {license_id or '未知'} 不允許直接附帶")
            else:
                warnings.append(f"略過選用的 {name}({f['path']}):CurseForge 上找不到相同檔案，授權 {license_id or '未知'} 不允許直接附帶")

    for w in warnings:
        print(f"注意:{w}", file=sys.stderr)
    if errors:
        sys.exit("無法產生 CurseForge 包(必裝的檔案放不進去):\n  " + "\n  ".join(errors))

    manifest = {
        "minecraft": {
            "version": pack["minecraft"],
            "modLoaders": [{"id": f"fabric-{pack['fabric-loader']}", "primary": True}],
        },
        "manifestType": "minecraftModpack",
        "manifestVersion": 1,
        "name": pack["name"],
        "version": pack["version"],
        "author": pack.get("author", ""),
        "files": sorted(manifest_files, key=lambda x: (x["projectID"], x["fileID"])),
        "overrides": "overrides",
    }
    modlist = "<ul>\n" + "".join(
        f"<li>{html.escape(path)} — {html.escape(note)}</li>\n" for path, note in sorted(listed)
    ) + "</ul>\n"

    args.out.mkdir(parents=True, exist_ok=True)
    out = args.out / f"{pack['name']}-{pack['version']}-curseforge.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        def add(arcname: str, data: bytes) -> None:
            info = zipfile.ZipInfo(arcname, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)

        add("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8"))
        add("modlist.html", modlist.encode("utf-8"))
        overrides = args.pack_dir / "overrides"
        if overrides.is_dir():
            for p in sorted(x for x in overrides.rglob("*") if x.is_file()):
                add(f"overrides/{p.relative_to(overrides).as_posix()}", p.read_bytes())
        for arcname, data in sorted(bundled.items()):
            add(arcname, data)

    via_cf = len(manifest_files)
    print(f"{out}:CurseForge 下載 {via_cf} 個、直接附帶 {len(bundled)} 個、略過 {len(warnings)} 個")


if __name__ == "__main__":
    main()
