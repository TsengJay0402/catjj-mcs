# catjj-mcs

catjj 主機上的 Minecraft 伺服器設定(Docker + [itzg/minecraft-server](https://github.com/itzg/docker-minecraft-server))。
世界存檔不在 repo 裡，由各服的備份機制負責。

| 資料夾 | 內容 | Port |
|---|---|---|
| [`techsmp/`](techsmp/說明.md) | 生電服:Fabric 26.3 + Carpet + Servux(Litematica Easy Place V3)+ 創造鏡像服 + 自動備份 | 25566 / 25567 |
| [`pekora/`](pekora/說明.md) | Pekora 地圖創造服:Paper 26.3 + WorldEdit | 25565 |
| [`reports/`](reports/) | 生電服核心選型研究報告(含引用來源) | — |
| `research_notes/` | 研究報告的原始筆記 | — |
| `tools/build-mrpack.py` | 從模組清單產生 Modrinth 模組包 `.mrpack` | — |

## 客戶端模組包
到 [Releases](https://github.com/TsengJay0402/catjj-mcs/releases) 下載 `TechSMP-<版本>.mrpack`,
用 Modrinth App 或 Prism Launcher 匯入即可。發布流程見 [`techsmp/說明.md`](techsmp/說明.md)。

## 新機器部署
```bash
git clone git@github.com:TsengJay0402/catjj-mcs.git && cd catjj-mcs/techsmp
cp .env.example .env && chmod 600 .env   # 填入 RCON_PASSWORD
docker compose up -d mc backup           # 生存服 + 備份
./refresh-mirror.sh                      # 第一次同步並啟動鏡像服
```
