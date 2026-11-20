# 客戶端效能提示

安裝包中的遠視距、光影、高解析材質和立體葉片皆為選用項目；視 GPU、CPU、顯存、Minecraft 分配記憶體、解析度與 shader 設定而定，可能降低 FPS 或增加載入時間。低階電腦建議只啟用需要的選項，一次啟用一項並測試。

| 選項 | 官方硬體建議 / 注意事項 |
|---|---|
| Distant Horizons | 官方卡頓排查建議：4–8 核 CPU 可嘗試分配 6–8 GB RAM；10+ 核可嘗試分配 12–16 GB 給 Minecraft。這是 Minecraft 記憶體分配建議，不是最低需求或整台電腦的 RAM 總量。降低 Graphics Preset、CPU Load 或關閉 Distant Generation 也能減少負荷。[官方說明](https://modrinth.com/mod/distanthorizons) |
| Iris 光影 | 各光影官方沒有統一的最低 PC 規格。Complementary 提供 Potato 到 Ultra 預設，建議先從 Potato／Low 開始；Bliss、Photon 也可調低畫質選項。[Complementary](https://modrinth.com/shader/complementary-reimagined) · [Bliss](https://modrinth.com/shader/bliss-shader) · [Photon](https://modrinth.com/shader/photon-shader) |
| ModernArch 128x | 約 255 MB。官方沒有公布最低電腦規格；高解析材質可能增加 GPU／顯存用量。[官方版本](https://modrinth.com/resourcepack/modernarch) |
| Optimized Bushy Leaves | 官方以效能為設計重點，建議啟用 Fancy／See-through Leaves，並搭配 More Culling 或同類功能；未列固定最低硬體規格。[官方說明](https://modrinth.com/resourcepack/fancyfast-bushy-leaves) |
| IterationT | 外部光影來源未列固定硬體規格；先用低畫質設定。 |

修改資源包時若遇到 Iris 渲染錯誤，先關閉光影再重新載入資源包，確認穩定後再逐一開回光影或遠視距選項。
