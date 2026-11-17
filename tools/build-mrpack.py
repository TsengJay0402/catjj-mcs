#!/usr/bin/env python3
"""從 mods.txt(slug:versionID 清單)產生 Modrinth 模組包 .mrpack。

用法:
    python3 tools/build-mrpack.py techsmp/client            # 產生 index 並打包到 dist/
    python3 tools/build-mrpack.py techsmp/client --check    # 只檢查 repo 裡的 index 是否最新(CI 用)

模組包資料夾需要:
    pack.json   名稱、版本、Minecraft 與 Fabric Loader 版本
    mods.txt    每行 <slug>:<Modrinth version ID> [optional],# 之後是註解
                沒標 optional 的客戶端必裝;標 optional 的在 index 裡是 env.client=optional
                (Prism Launcher 匯入時讓玩家勾選，Modrinth App 目前會全部安裝)
                可以放模組、光影包、資源包，路徑依 Modrinth 專案類型自動決定
    overrides/  (選用)要原樣放進客戶端 .minecraft 的檔案，例如預設設定檔

產物:
    <pack>/modrinth.index.json   會 commit 進 repo,升級時 diff 看得到檔名和雜湊變化
    dist/<name>-<version>.mrpack 用 Modrinth App / Prism Launcher 匯入
只使用標準函式庫，不需要額外安裝套件。
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

API = "https://api.modrinth.com/v2"
USER_AGENT = "catjj-mcs/build-mrpack (github.com/TsengJay0402/catjj-mcs)"
ZIP_TIMESTAMP = (2020, 1, 1, 0, 0, 0)  # 固定時間戳，讓同樣輸入產生同樣的 zip
FOLDERS = {"mod": "mods", "shader": "shaderpacks", "resourcepack": "resourcepacks"}
FLAGS = {"optional"}


def api_get(path: str, **params: object) -> object:
    query = urllib.parse.urlencode({k: json.dumps(v) for k, v in params.items()})
    req = urllib.request.Request(f"{API}{path}?{query}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def read_mods(path: Path) -> list[tuple[str, str, bool]]:
    """回傳 (slug, versionID, 是否選用)。"""
    mods = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        tokens = raw.split("#", 1)[0].split()
        if not tokens:
            continue
        slug, sep, version_id = tokens[0].partition(":")
        flags = set(tokens[1:])
        if not sep or not slug or not version_id or flags - FLAGS:
            sys.exit(f"{path}:{lineno}: 格式應為 <slug>:<versionID> [optional],實際是 {raw!r}")
        mods.append((slug, version_id, "optional" in flags))
    return mods


def build_index(pack_dir: Path) -> dict:
    pack = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    mods = read_mods(pack_dir / "mods.txt")
    mc, loader = pack["minecraft"], pack["fabric-loader"]

    versions = {v["id"]: v for v in api_get("/versions", ids=[vid for _, vid, _ in mods])}
    projects = {p["id"]: p for p in api_get("/projects", ids=sorted({v["project_id"] for v in versions.values()}))}

    errors: list[str] = []
    warnings: list[str] = []
    files = []
    listed: dict[str, tuple[str, str, bool]] = {}  # project_id -> (slug, versionID, 選用)
    for slug, vid, optional in mods:
        v = versions.get(vid)
        if v is None:
            errors.append(f"{slug}: 找不到版本 {vid}")
            continue
        p = projects[v["project_id"]]
        if p["id"] in listed:
            errors.append(f"{slug}: 重複列出")
        listed[p["id"]] = (slug, vid, optional)
        if p["slug"] != slug:
            errors.append(f"{slug}: 版本 {vid} 屬於 {p['slug']},不是 {slug}")
        if p["project_type"] not in FOLDERS:
            errors.append(f"{slug}: 不支援的專案類型 {p['project_type']}")
            continue
        if mc not in v["game_versions"]:
            errors.append(f"{slug} {v['version_number']}: 不支援 Minecraft {mc}(支援 {v['game_versions']})")
        if p["project_type"] == "mod" and "fabric" not in v["loaders"]:
            errors.append(f"{slug} {v['version_number']}: 不是 Fabric 版(loaders={v['loaders']})")
        if p["project_type"] == "shader" and "iris" not in v["loaders"]:
            errors.append(f"{slug} {v['version_number']}: 不是 Iris 可用的光影(loaders={v['loaders']})")
        f = next((f for f in v["files"] if f.get("primary")), v["files"][0])
        if p["project_type"] == "mod" and p["server_side"] in ("required", "optional", "unsupported"):
            server = p["server_side"]
        else:
            server = "unsupported" if p["project_type"] != "mod" else "optional"
        files.append({
            "path": f"{FOLDERS[p['project_type']]}/{f['filename']}",
            "hashes": {"sha1": f["hashes"]["sha1"], "sha512": f["hashes"]["sha512"]},
            # 這是客戶端模組包:client 由 mods.txt 決定(必裝/選用);server 照 Modrinth 專案標示
            "env": {"client": "optional" if optional else "required", "server": server},
            "downloads": [f["url"]],
            "fileSize": f["size"],
        })

    missing: list[tuple[str, str]] = []
    for slug, vid, optional in mods:
        v = versions.get(vid)
        for dep in (v or {}).get("dependencies", []):
            if dep["dependency_type"] != "required":
                continue
            dep_project = dep.get("project_id") or versions.get(dep.get("version_id"), {}).get("project_id")
            if not dep_project:
                continue
            if dep_project not in listed:
                missing.append((slug, dep_project))
                continue
            dep_slug, dep_vid, dep_optional = listed[dep_project]
            if dep_optional and not optional:
                errors.append(f"{slug}(必裝)依賴 {dep_slug}(選用):把 {dep_slug} 改成必裝")
            if dep.get("version_id") and dep["version_id"] != dep_vid:
                warnings.append(f"{slug} 在 Modrinth 上標示需要 {dep_slug} 的版本 {dep['version_id']},清單裡是 {dep_vid}")
    if missing:
        dep_projects = {p["id"]: p for p in api_get("/projects", ids=sorted({d for _, d in missing}))}
        for slug, dep_project in missing:
            dp = dep_projects.get(dep_project)
            if dp and "fabric" not in dp.get("loaders", []):
                # Modrinth 上偶爾會把其他載入器的依賴標到 Fabric 版(例如 Zoomify 標了 Forge 專用的 KotlinLangForge)
                warnings.append(f"{slug}: 略過 Modrinth 標示的依賴 {dp['slug']}(沒有 Fabric 版，應是標錯)")
            else:
                errors.append(f"{slug}: 缺少必要依賴 {dp['slug'] if dp else dep_project}")

    for w in warnings:
        print(f"注意:{w}", file=sys.stderr)
    if errors:
        sys.exit("模組清單有問題:\n  " + "\n  ".join(errors))

    return {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": pack["version"],
        "name": pack["name"],
        "summary": pack.get("summary", ""),
        "files": sorted(files, key=lambda x: x["path"]),
        "dependencies": {"minecraft": mc, "fabric-loader": loader},
    }


def write_mrpack(pack_dir: Path, index: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{index['name']}-{index['versionId']}.mrpack"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        def add(arcname: str, data: bytes) -> None:
            info = zipfile.ZipInfo(arcname, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)

        add("modrinth.index.json", json.dumps(index, indent=2, ensure_ascii=False).encode("utf-8"))
        overrides = pack_dir / "overrides"
        if overrides.is_dir():
            for f in sorted(p for p in overrides.rglob("*") if p.is_file()):
                add(f"overrides/{f.relative_to(overrides).as_posix()}", f.read_bytes())
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack_dir", type=Path)
    ap.add_argument("--out", type=Path, default=Path("dist"), help="mrpack 輸出資料夾(預設 dist/)")
    ap.add_argument("--check", action="store_true", help="只檢查 modrinth.index.json 是否和 mods.txt 一致，不寫檔")
    args = ap.parse_args()

    index = build_index(args.pack_dir)
    index_path = args.pack_dir / "modrinth.index.json"
    rendered = json.dumps(index, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        current = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
        if current != rendered:
            sys.exit(f"{index_path} 不是最新的，請執行 python3 tools/build-mrpack.py {args.pack_dir} 後再 commit")
        print(f"OK: {index_path} 與 mods.txt 一致({len(index['files'])} 個檔案)")
        return

    index_path.write_text(rendered, encoding="utf-8")
    out = write_mrpack(args.pack_dir, index, args.out)
    optional = sum(f["env"]["client"] == "optional" for f in index["files"])
    print(f"{index['name']} {index['versionId']}:{len(index['files'])} 個檔案(選用 {optional})→ {index_path}、{out}")
    for f in index["files"]:
        print(f"  {f['path']:<60} client={f['env']['client']:<8} server={f['env']['server']}")


if __name__ == "__main__":
    main()
