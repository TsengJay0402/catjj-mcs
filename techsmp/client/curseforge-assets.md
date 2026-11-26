# CurseForge / 手動安裝內容

不存放任何下載檔，只保留來源與本機 SHA-256。IterationT、Lodeways 和 Backpackery 由 `external-assets.json` 以 CurseForge 官方 CDN 連結加入 `.mrpack`；其他項目仍需從其來源手動安裝。

| 類型 | 項目 | 版本 | 官方來源 | CurseForge ID / File ID | SHA-256 | 備註 |
|---|---|---|---|---|---|---|
| 光影 | IterationT | 3.2.0 | [CurseForge](https://www.curseforge.com/minecraft/shaders/interationrp) | `1546329` / `8105693` | `C0735D5F1DE0EDCA2B1C155DAE1C650DDB8D2D04A3EBDD3D2FF74DD7A19DB116` | 已由 `.mrpack` 外部下載連結安裝；來源未列固定硬體規格，從低畫質開始測試 |
| 模組 | Lodeways | 1.20.0 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/lodeways-waystones) | `1739944` / `9712118` | `AC52B833385A2A45EA9710BCC732972DC4B9AB809384EDEA6C013E0939EC3F00` | Fabric 26.3；客戶端與伺服器都要安裝；已加入伺服器設定及 `.mrpack` |
| 模組 | Backpackery | 2.3.5 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/backpackery) | `1764739` / `9372945` | `20F58A05B2978C367358158819BC1D99CB726E09584FCFF51DF174CCA6568B84` | Fabric 26.3；CurseForge 頁面標示 Client，但 jar 的 `fabric.mod.json` 為 `environment: "*"` 且在共用端註冊物品與選單，客戶端與伺服器都要安裝；已加入伺服器設定及 `.mrpack` |
| 資源包 | LowOnFire | 1.2 | 原始下載來源未記錄 | — | `25FC89FEDC6D47FE2480A60910C65C8FD8B50121AAAB919933E47CC6BA730A67` | 內附說明署名 Haikis；保留本機記錄，需取得原始來源才能自動安裝 |
