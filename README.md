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
| `tools/level-info.py` | 檢查世界資料夾的版本、結構與搬遷步驟 | — |

## 客戶端模組包
到 [Releases](https://github.com/TsengJay0402/catjj-mcs/releases) 下載 `TechSMP-<版本>.mrpack`,
用 Modrinth App 或 Prism Launcher 匯入即可。發布流程見 [`techsmp/說明.md`](techsmp/說明.md)。

## 部署到正式主機
請看 [`techsmp/部署說明.md`](techsmp/部署說明.md):主機需求、deploy key、放入既有地圖、第一次啟動、日常維運。
`tools/level-info.py <世界資料夾>` 可以檢查地圖版本和資料夾結構(唯讀)。
