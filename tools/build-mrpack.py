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
    external-assets.json (選用)提供非 Modrinth 素材的官方 HTTPS 下載連結和 SHA-1/SHA-512
    overrides/  (選用)要原樣放進客戶端 .minecraft 的檔案，例如預設設定檔

產物:
    <pack>/modrinth.index.json   會 commit 進 repo,升級時 diff 看得到檔名和雜湊變化
    dist/<name>-<version>.mrpack 用 Modrinth App / Prism Launcher 匯入
    dist/packwiz/                packwiz 格式(pack.toml、index.toml、*.pw.toml),
                                 發佈 tag 時由 CI 推到 techsmp-client-pack 分支，給 Prism + packwiz-installer 自動更新用
                                 選用模組的說明取自 mods.txt 該行 # 之後的註解
只使用標準函式庫，不需要額外安裝套件。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

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


def read_comments(path: Path) -> dict[str, str]:
    """回傳 slug -> 該行 # 之後的註解(給 packwiz 選用模組視窗當說明)。"""
    comments = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        code, _, comment = raw.partition("#")
        tokens = code.split()
        if tokens:
            comments[tokens[0].partition(":")[0]] = comment.strip()
    return comments


def build_index(pack_dir: Path) -> tuple[dict, dict[str, dict]]:
    """回傳 (modrinth.index.json 內容, 每個檔案路徑的額外資訊)。額外資訊只給 packwiz 用，不進 index。"""
    pack = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    mods = read_mods(pack_dir / "mods.txt")
    comments = read_comments(pack_dir / "mods.txt")
    meta: dict[str, dict] = {}
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
        meta[f"{FOLDERS[p['project_type']]}/{f['filename']}"] = {
            "id": slug,
            "name": p["title"],
            "description": comments.get(slug, ""),
            "update": ("modrinth", {"mod-id": p["id"], "version": vid}),
        }
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

    external_path = pack_dir / "external-assets.json"
    if external_path.exists():
        try:
            external_manifest = json.loads(external_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{external_path}: 無法讀取 JSON ({exc})")
            external_manifest = {}
        external_files = external_manifest.get("files") if isinstance(external_manifest, dict) else None
        if not isinstance(external_files, list):
            errors.append(f"{external_path}: files 必須是陣列")
        else:
            paths = {f["path"] for f in files}
            env_values = {"required", "optional", "unsupported"}
            for index, asset in enumerate(external_files, 1):
                label = f"{external_path}:files[{index - 1}]"
                if not isinstance(asset, dict):
                    errors.append(f"{label}: 每個素材都必須是物件")
                    continue
                path = asset.get("path")
                url = asset.get("url")
                hashes = asset.get("hashes")
                size = asset.get("fileSize")
                env = asset.get("env")
                source = asset.get("source")
                if not isinstance(path, str) or not path or "\\" in path:
                    errors.append(f"{label}: path 必須是相對 POSIX 路徑")
                    continue
                asset_path = PurePosixPath(path)
                if (asset_path.is_absolute() or path != asset_path.as_posix()
                        or ".." in asset_path.parts
                        or not asset_path.parts
                        or asset_path.parts[0] not in FOLDERS.values()):
                    errors.append(f"{label}: 不允許的路徑 {path!r}")
                    continue
                parsed_url = urllib.parse.urlparse(url) if isinstance(url, str) else None
                if not parsed_url or parsed_url.scheme != "https" or not parsed_url.netloc:
                    errors.append(f"{label}: url 必須是 HTTPS 下載連結")
                    continue
                if not isinstance(hashes, dict):
                    errors.append(f"{label}: hashes 必須包含 SHA-1 和 SHA-512")
                    continue
                sha1, sha512 = hashes.get("sha1"), hashes.get("sha512")
                if (not isinstance(sha1, str) or len(sha1) != 40
                        or not isinstance(sha512, str) or len(sha512) != 128
                        or any(c not in "0123456789abcdefABCDEF" for c in sha1 + sha512)):
                    errors.append(f"{label}: SHA-1/SHA-512 格式錯誤")
                    continue
                if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
                    errors.append(f"{label}: fileSize 必須是正整數")
                    continue
                if (not isinstance(env, dict)
                        or not isinstance(env.get("client"), str)
                        or env.get("client") not in env_values
                        or not isinstance(env.get("server"), str)
                        or env.get("server") not in env_values):
                    errors.append(f"{label}: env.client/env.server 值錯誤")
                    continue
                if not isinstance(source, str) or not source.strip():
                    errors.append(f"{label}: source 必須註明官方來源")
                    continue
                if path in paths:
                    errors.append(f"{label}: 重複的檔案路徑 {path!r}")
                    continue
                paths.add(path)
                cf = re.fullmatch(r"CurseForge project (\d+), file (\d+)", source.strip())
                stem = PurePosixPath(path).stem
                meta[path] = {
                    "id": re.sub(r"[^a-z0-9.-]+", "-", stem.lower()).strip("-"),
                    "name": stem,
                    "description": source.strip(),
                    "update": ("curseforge", {"project-id": int(cf[1]), "file-id": int(cf[2])}) if cf else None,
                }
                files.append({
                    "path": path,
                    "hashes": {"sha1": sha1.lower(), "sha512": sha512.lower()},
                    "env": env,
                    "downloads": [url],
                    "fileSize": size,
                })

    for w in warnings:
        print(f"注意:{w}", file=sys.stderr)
    if errors:
        sys.exit("模組清單有問題:\n  " + "\n  ".join(errors))

    index = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": pack["version"],
        "name": pack["name"],
        "summary": pack.get("summary", ""),
        "files": sorted(files, key=lambda x: x["path"]),
        "dependencies": {"minecraft": mc, "fabric-loader": loader},
    }
    return index, meta


def toml_str(value: str) -> str:
    # JSON 字串的跳脫(\" \\ \n \uXXXX)也是合法的 TOML basic string
    return json.dumps(value, ensure_ascii=False)


def write_packwiz(pack_dir: Path, index: dict, meta: dict[str, dict], out_dir: Path) -> Path:
    """依 packwiz 格式(https://packwiz.infra.link/reference/pack-format/)輸出整個模組包資料夾。"""
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    entries: list[tuple[str, str, bool]] = []  # (相對路徑, sha256, 是否為 metafile)

    def put(rel: str, data: bytes, metafile: bool) -> None:
        target = out_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        entries.append((rel, hashlib.sha256(data).hexdigest(), metafile))

    used: set[str] = set()
    for f in index["files"]:
        m = meta[f["path"]]
        folder, filename = f["path"].rsplit("/", 1)
        rel = f"{folder}/{m['id']}.pw.toml"
        if rel in used:
            sys.exit(f"packwiz: 檔名重複 {rel}")
        used.add(rel)
        # 這是客戶端模組包；伺服器也要裝的標成 both,packwiz-installer 預設(client 端)兩種都會裝
        side = "both" if f["env"]["server"] in ("required", "optional") else "client"
        lines = [
            f"name = {toml_str(m['name'])}",
            f"filename = {toml_str(filename)}",
            f"side = {toml_str(side)}",
            "",
            "[download]",
            f"url = {toml_str(f['downloads'][0])}",
            'hash-format = "sha512"',
            f"hash = {toml_str(f['hashes']['sha512'])}",
        ]
        if f["env"]["client"] == "optional":
            # 和 .mrpack 在 Prism 的行為一致：選用模組預設不勾
            lines += ["", "[option]", "optional = true", "default = false"]
            if m["description"]:
                lines.append(f"description = {toml_str(m['description'])}")
        if m["update"]:
            source, fields = m["update"]
            lines += ["", f"[update.{source}]"]
            lines += [f"{k} = {toml_str(v) if isinstance(v, str) else v}" for k, v in fields.items()]
        put(rel, ("\n".join(lines) + "\n").encode("utf-8"), metafile=True)

    overrides = pack_dir / "overrides"
    if overrides.is_dir():
        for p in sorted(x for x in overrides.rglob("*") if x.is_file()):
            put(p.relative_to(overrides).as_posix(), p.read_bytes(), metafile=False)

    index_lines = ['hash-format = "sha256"']
    for rel, digest, metafile in sorted(entries):
        index_lines += ["", "[[files]]", f"file = {toml_str(rel)}", f"hash = {toml_str(digest)}"]
        if metafile:
            index_lines.append("metafile = true")
    index_data = ("\n".join(index_lines) + "\n").encode("utf-8")
    (out_dir / "index.toml").write_bytes(index_data)

    pack_toml = "\n".join([
        f"name = {toml_str(index['name'])}",
        f"version = {toml_str(index['versionId'])}",
        'pack-format = "packwiz:1.1.0"',
        "",
        "[index]",
        'file = "index.toml"',
        'hash-format = "sha256"',
        f"hash = {toml_str(hashlib.sha256(index_data).hexdigest())}",
        "",
        "[versions]",
        f"minecraft = {toml_str(index['dependencies']['minecraft'])}",
        f"fabric = {toml_str(index['dependencies']['fabric-loader'])}",
    ]) + "\n"
    (out_dir / "pack.toml").write_text(pack_toml, encoding="utf-8", newline="\n")
    return out_dir


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

    index, meta = build_index(args.pack_dir)
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
    pw = write_packwiz(args.pack_dir, index, meta, args.out / "packwiz")
    optional = sum(f["env"]["client"] == "optional" for f in index["files"])
    print(f"{index['name']} {index['versionId']}:{len(index['files'])} 個檔案(選用 {optional})→ {index_path}、{out}、{pw}")
    for f in index["files"]:
        print(f"  {f['path']:<60} client={f['env']['client']:<8} server={f['env']['server']}")


if __name__ == "__main__":
    main()
