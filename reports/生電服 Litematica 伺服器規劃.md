# 用 Fabric＋Servux 撐起 26.3 生電服

截至 2026-11-17，要在 Minecraft Java 26.3 上開一台以 Litematica 生存建築為主的生電服，可行的組合實際上只有一種：**原版 Fabric 伺服器加 Carpet、Carpet TIS Addition、Servux 0.12.2、Syncmatica 0.3.20 和 Lithium**。原因是 Easy Place Protocol V3 把方塊狀態編碼在「use item on block」封包的點擊座標裡，原版和 Paper 的伺服器會把這種座標當成非法封包丟掉，結果就是幽靈方塊。26.3 上唯一還在維護、能在伺服器端解開 V3 的是 Servux 的 mixin。原本走 V2 的 Carpet Extra 沒有 26.3 版本，Leaves 停在 1.21.11，Paper 系那些補 V3 的插件最新也只到 26.2。Fabric 這條線也剛好最貼近原版：Carpet 和 TIS Addition 預設不改原版機制，Lithium 把少數偏離原版的最佳化列成可以關閉的選項。管理工具改用 Ledger（回滾）、itzg/mc-backup（整個世界快照）和一台 Fabric 創造鏡像服。你的 12 核、125 GB 主機跑 4–8 人遠遠過剩，效能不是選核心時的考量。以下依序說明 V3 為什麼非得在伺服器端處理、各核心在 26.3 的實際狀況、原版相容與效能的取捨、管理生態，最後給出推薦方案、各情境下的替代方案，以及可以直接照做的 docker compose 部署步驟（新服用 port 25566，鏡像服用 25567）。

## Easy Place V3 只能靠伺服器端 Servux 解開

Easy Place 會把目標方塊狀態寫進點擊位置的 X 座標，公式是 `hitX = blockX + 2 + protocolValue`。伺服器端拿 `(int)(hitVec.x - pos.getX()) - 2` 解出 protocolValue。數值小於 0 就當成一般點擊，大於等於 0 時，第 1–3 bit 是朝向，其餘屬性依名稱字母順序逐一占用 bit。白名單涵蓋 FACING、AXIS、HALF、CHEST_TYPE、DOOR_HINGE、RAIL_SHAPE、STAIRS_SHAPE、MODE_COMPARATOR、DELAY、NOTE、ROTATION_16、ORIENTATION（crafter）等。另外有三條硬性限制：WATERLOGGED 和 POWERED 強制為 false，雙層半磚一律拒絕（防止複製）([PlacementHandler.java](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/util/PlacementHandler.java))。問題在於**原版從 1.18.2 起，伺服器只接受點擊位置與方塊中心相距不到約 1 格的封包**。Litematica 自己的設定說明也寫著，這個檢查會讓「帶旋轉或其他屬性要求的方塊直接變成幽靈方塊」([Litematica en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json))。Litematica 客戶端的 `itemUsePacketCheckBypass` 只作用於單人遊戲的內建伺服器 ([Mixin 原始碼](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/mixin/easyplace/MixinServerGamePacketListenerImpl_easyPlace.java))，所以多人遊戲一定要由伺服器端解碼。

**Servux 0.12.2（2026-09-27，26.3）** 在伺服器端對 `BlockItem#getPlacementState` 注入 priority 950 的 mixin。原始碼註解寫明它刻意蓋過 Carpet Extra 的版本。玩家有權限時，它會套用 `applyPlacementProtocolV3`，並附帶對應的封包距離檢查繞過 ([MixinBlockItem_EasyPlace.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/mixin/easy_place/MixinBlockItem_EasyPlace.java))。相關設定在 `servux_main` 底下：`permission_level_easy_place` 預設 **0**（所有玩家都能用），`easy_place_validator_enabled` 預設 true ([ServuxConfigProvider.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/dataproviders/ServuxConfigProvider.java))。客戶端的 Auto 模式在程式碼裡比遊戲內說明文字新：偵測到 Servux 伺服器就直接選 V3，只有 Carpet（`carpet:hello`）時選 V2，兩者都沒有時退回「Slabs only」([PlacementHandler.java](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/util/PlacementHandler.java))。V2 那條路在 26.3 已經斷了。`accurateBlockPlacement` 是 Carpet **Extra** 的規則，不在 Carpet 本體 ([carpet-extra README](https://raw.githubusercontent.com/gnembon/carpet-extra/master/README.md))，而 Carpet Extra 最新只到 26.2，jar 裡寫死 `"minecraft": "26.2.x"`，Fabric Loader 在 26.3 會拒絕載入 ([Modrinth carpet-extra](https://api.modrinth.com/v2/project/carpet-extra/version))。V2 本身也只能處理朝向、軸向、中繼器延遲、比較器模式和上下半，箱子的單雙、門軸、鐵軌形狀這些都要 V3 才有。

在 Paper 或原版伺服器上，Auto 會落到 Slabs only。這時只有上半磚會放對，樓梯、偵測器、活塞、漏斗、中繼器、比較器、鐵軌、雙箱、門和原木軸向全看玩家當下的視角。硬把協定設成 V2 或 V3 反而全部變成幽靈方塊。這是從上述程式碼和 1.18.2 檢查推出來的結論，Litematica wiki 也明說不要在沒有伺服器支援的伺服器上硬設 V2 或 V3 ([Litematica wiki: Easy Place](https://github.com/maruohon/litematica/wiki/Easy-Place))。

Servux 也提供 Easy Place 以外的伺服器端功能。**存檔時要帶進箱子內容等 NBT**，需要 Servux `entity_data` 加上客戶端開啟 `entityDataSync`（預設**關閉**）。不用 Servux 的備援 `entityDataSyncBackup` 需要 OP。**伺服器端快速貼上**需要 Servux `litematic_data`，而且從 0.9.7 起限定創造模式 ([Servux 版本紀錄](https://api.modrinth.com/v2/project/servux/version))。MiniHUD 的結構框來自 `structure_bounding_boxes`，種子、天氣、TPS 和 mob cap 來自 `hud_data`，但**種子預設只分享給權限 ≥2 的玩家** ([HudDataProvider.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/dataproviders/HudDataProvider.java))。投影共享是另一個獨立的模組 Syncmatica，伺服器和客戶端都要裝 ([Modrinth Syncmatica 26.3](https://api.modrinth.com/v2/project/syncmatica/version?game_versions=%5B%2226.3%22%5D))。這些 26.3 版 masa 系模組都由 sakura-ryoko 維護。masa 本人 2024 年就表示 1.20.4 之後不再更新舊架構的程式碼，Modrinth 上的官方 Litematica 指向的正是 sakura-ryoko 的 repo ([Modrinth litematica](https://api.modrinth.com/v2/project/litematica))。

## 26.3 上只有 Fabric 線同時具備核心與協定

下表整理 2026-11-17 各伺服器核心在 26.3 的實際狀態。重點是「有 26.3 版本」和「能讓 V3 正常運作」兩個條件要同時成立。

| 核心 | 26.3 版本 | Easy Place V3 | Servux 資料／貼上 | Syncmatica／PCA | 原版行為 | 判斷 |
|---|---|---|---|---|---|---|
| **Fabric + Carpet + Servux** | Carpet 26.3（2026-09-18）、Servux 0.12.2、Fabric API 0.166.2 | **原生支援**（Servux mixin） | 完整 | Syncmatica 0.3.20；pca-protocol v0.3.15 | 以原版為基準 | **推薦** |
| Leaves | **沒有任何 26.x**，最新 1.21.11-157（2026-08-13） | 1.21.11 有 `LITEMATICA` 選項 | 內建模擬 | 內建 | 開技術生存模式後還原大部分 | 26.3 不能用 |
| Paper | build 253（2026-11-15，STABLE） | 沒有；要靠插件，插件尚無 26.3 版 | 沒有（LitematicaFolia 只到 26.2） | 需另找插件 | 官方承認做不到 100% 原版 | 不建議 |
| Purpur | build 2659（2026-11-16） | 沒有 | 沒有 | — | Paper 之上再加玩法改動 | 不建議 |
| Folia | build 8（2026-11-15） | 沒有 | 沒有 | — | 區域多執行緒，建議 ≥16 核 | 不適合 |
| Lophine | 26.3 tag（2026-11-15） | 移植了 Leaves 的 patch，**未經獨立驗證** | 部分 | 有 | Folia 基底，README 自己說完整生電請用 Fabric | 實驗性 |
| Leaf | 26.3（2026-11-16） | 沒有 | 沒有 | 只有 Syncmatica | 偏重效能 | 不建議 |
| DivineMC | 26.3 #7（2026-11-15） | 沒有 | 沒有 | 只有 Syncmatica | 平行世界 tick、非同步生怪 | 不建議 |
| Canvas | 26.3（Folia fork） | 沒有 | 沒有 | — | 區域多執行緒 | 不適合 |
| Gale／Pufferfish／Luminol | 26.2／1.21／repo 404 | — | — | — | — | 不能用 |

表中資料的來源如下：Fabric 線見 [Modrinth carpet](https://api.modrinth.com/v2/project/carpet/version) 和 [servux](https://api.modrinth.com/v2/project/servux/version)；Leaves 見 [Leaves API](https://api.leavesmc.org/v2/projects/leaves)；Paper 見 [fill.papermc.io](https://fill.papermc.io/v3/projects/paper/versions/26.3/builds/latest)；Purpur 見 [Purpur API](https://api.purpurmc.org/v2/purpur/26.3/latest)；Folia 見 [Folia README](https://raw.githubusercontent.com/PaperMC/Folia/ver/26.3.x/README.md)；Lophine 見 [Lophine README](https://raw.githubusercontent.com/LophineLabs/Lophine/ver/26.3/README.md)；Leaf 見 [Leaf 設定文件](https://www.leafmc.one/docs/config/leaf-global)；DivineMC 見 [DivineMC README](https://raw.githubusercontent.com/BX-Team/DivineMC/ver/26.3/README.md)；Gale 見 [Gale releases](https://github.com/GaleMC/Gale/releases)。

**Leaves 書面上的功能最完整**：`alternative-block-placement: LITEMATICA` 支援 V3，此外有 Servux 結構／實體／HUD／投影協定、Syncmatica、PCA、BBOR、Jade、假人，以及一鍵關掉 Paper 防刷修正的 `mc-technical-survival-mode` ([LeavesConfig.java](https://raw.githubusercontent.com/LeavesMC/Leaves/master/leaves-server/src/main/java/org/leavesmc/leaves/LeavesConfig.java))。但它更新落後很多。26.1 的 PR #846 沒有合併就關閉了，26.1.2 的 PR #863 到 2026-09-10 還開著，請求 26.x 的 issue 被標成重複後關閉，沒有給任何時程 ([PR #863](https://github.com/LeavesMC/Leaves/pull/863)；[Issue #871](https://github.com/LeavesMC/Leaves/issues/871))。從 1.21.11 到 26.3 要連跳三個版本，主分支最後一次 commit 是 2026-08-13。我的判斷是專案停滯但沒有死。itzg 映像檔也**沒有 `TYPE=LEAVES`**，只能用 `TYPE=CUSTOM` ([itzg scripts](https://github.com/itzg/docker-minecraft-server/tree/master/scripts))。

**Paper 本身**的官方文件直說「目前不可能在 Paper 得到 100% 原版體驗」，也承認技術型玩家的機器可能無法正常運作 ([Paper vanilla 指南](https://docs.papermc.io/paper/vanilla/))。補 V3 的插件有 Paper Accurate Block Placement（支援 V2/V3，需要 PacketEvents，最新 1.4.0 只到 26.2）([Modrinth](https://modrinth.com/plugin/paper-accurate-block-placement)) 和 VeryMcProto（Servux、Syncmatica、Carpet 子集、EasyPlace，最新 26.2-b4，綁定 NMS）([Modrinth](https://modrinth.com/plugin/verymcproto))。26.2 的 jar 在 26.3 能不能載入沒有人測過。**Lophine** 是 26.3 上唯一繼承 Leaves 協定 patch 的分支，包括 Alternative block placement、Servux、Syncmatica、PCA、假人和更新抑制 ([Lophine 26.3 patches](https://github.com/LophineLabs/Lophine/tree/ver/26.3/lophine-server/minecraft-patches/features))。但它建在 Folia 上，Folia 要求「至少 16 核」，而且幾乎所有 Paper 插件都要改過才能用 ([Folia README](https://raw.githubusercontent.com/PaperMC/Folia/ver/26.3.x/README.md))。Luminol 文件也警告，Folia 系的原版特性還原「仍然非常有限」([Luminol docs](https://luminol-docs-neo.pages.dev/en/guide/luminol))。你的主機是 12 核，Lophine 自己的 README 也寫著「完整生電請使用 Fabric」，所以不值得冒這個險。

## 原版相容看 Lithium 怎麼設定，效能不是瓶頸

Fabric 線的原版相容來自各模組「預設不動原版」的承諾。Carpet TIS Addition 的 README 寫明預設設定不改任何原版行為 ([TIS README](https://raw.githubusercontent.com/TISUnion/Carpet-TIS-Addition/master/README.md))，Carpet Org Addition 的所有功能也都要手動開啟 ([Modrinth](https://modrinth.com/mod/carpet-org-addition))。Carpet 本體有少數規則開了就不再是原版，例如 `fastRedstoneDust` 會修正 MC-11193 的位置性行為 ([Carpet 規則列表](https://raw.githubusercontent.com/wiki/gnembon/fabric-carpet/Current-Available-Settings.md))，保持預設關閉即可。Servux 有一個容易忽略的非原版預設：`entity_data` 的 **`fix_allay_gathering` 預設 true**，只在 `mobGriefing=false` 時生效，但想要嚴格原版就該關掉 ([EntitiesDataProvider.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/dataproviders/EntitiesDataProvider.java))。

**Lithium（mc26.3-0.26.3，2026-10-28）**是唯一建議預設就裝的伺服器效能模組。它的目標是「不改變任何原版機制」，偏離原版的部分都集中在 `mixin.minimal_nonvanilla.*` 底下，共五項：蛙的視線快取、1e-7 格內的碰撞位置、生怪密度浮點加總的順序、漏斗的方塊狀態快取、區塊卸載順序。官方把這些造成的機器故障視為 bug ([lithium mixin config](https://raw.githubusercontent.com/CaffeineMC/lithium/mc26.3-0.26.3/lithium-fabric-mixin-config.md))。如果有玩家在研究生怪率或區塊卸載順序，可以把 `mixin.minimal_nonvanilla` 整組關掉。漏斗快取歷史上出過 bug，所以漏斗相關的機器出現怪異行為時，要把 Lithium 列為嫌疑之一。FerriteCore 9.0.0 只優化記憶體，可以放心裝。**C2ME 和 ScalableLux 在 26.3 都還是 alpha** ([c2me](https://api.modrinth.com/v2/project/c2me-fabric/version)；[scalablelux](https://api.modrinth.com/v2/project/scalablelux/version))，又分別動到區塊載入和光照，正好是生電玩家會去碰的機制，建議先不要裝。上游 ModernFix 沒有 Fabric 26.x 版本，Noisium 已經停止維護，這兩個直接跳過。

Paper 系的效能優勢在這個規模用不上，還會帶來原版差異。Paper 的封包限制器預設 7 秒 500 個封包、超過就踢人，Easy Place 連點和 printer 很容易觸發。spigot 的 entity activation range、每玩家生怪上限和延遲卸載區塊，也都要依 vanilla 指南一項一項改回去 ([Paper 全域設定](https://docs.papermc.io/paper/reference/global-configuration/))。DivineMC 的平行世界 tick 和非同步生怪會改變 tick 的執行順序，對農場來說風險大於收益。這是推論，目前沒有實測資料。4–8 人在 12 核主機上，給 10 GB heap 的原版單執行緒 tick 已經綽綽有餘。itzg 建議容器的記憶體上限比 heap 多留約 25% ([itzg JVM 文件](https://docker-minecraft-server.readthedocs.io/en/latest/configuration/jvm-options/))。

有一個與核心無關、但會影響農場設計的 26.x 現實：**生成區塊（spawn chunks）在 1.21.9 已經移除**，常駐載入只能靠玩家、Carpet 假人或 `/forceload` ([Minecraft Wiki](https://minecraft.wiki/w/Spawn_chunks))。另外，從 1.21.2 起伺服器在沒人時會自動暫停（`pause-when-empty-seconds`），這會讓掛機農場停擺 ([itzg autopause 文件](https://github.com/itzg/docker-minecraft-server/blob/master/docs/misc/autopause-autostop/autopause.md))。

## 管理、備份、回滾在 Fabric 上要自己組

插件生態是 Paper 線唯一明顯勝出的地方，但在 26.3 上這個優勢比想像中小。**CoreProtect 正式版 24.1 只支援到 26.2**，維護者在 issue 中把使用者導向 Patreon 上的 v25 預編譯版 ([Issue #1044](https://github.com/PlayPro/CoreProtect/issues/1044))。Fabric 端的對應工具在 26.3 都有正式版：**Ledger 1.3.25**（類似 CoreProtect 的紀錄與回滾，需要 Fabric Language Kotlin）、LuckPerms v5.5.85-fabric、fabric-permissions-api 0.7.0、Chunky 1.5.66、BlueMap 5.29、squaremap 1.4.3 ([Modrinth ledger](https://api.modrinth.com/v2/project/ledger/version)；[luckperms](https://api.modrinth.com/v2/project/luckperms/version))。缺的是備份模組：**Textile Backup 和 X Backup 都沒有 26.x 版本** ([textile_backup](https://api.modrinth.com/v2/project/textile_backup/version)；[x-backup](https://api.modrinth.com/v2/project/x-backup/version))。在 itzg 體系下，最穩的做法是用 **itzg/mc-backup** sidecar。它透過 RCON 下 `save-off`／`save-all`，支援 tar、rsync、restic、rclone，以及間隔、清理和排除規則 ([docker-mc-backup](https://github.com/itzg/docker-mc-backup))，完全不受模組版本影響。

中文生電圈的傳統架構是 Fabric 加 MCDR，前面再接 Velocity 把生存、鏡像、創造串起來 ([aimerny 教學](https://aimerny.top/2023/09/25/mcdr/mcdr-tutor-1-pre/))。MCDR 本身很活躍，v2.16.3 在 2026-11-10 發布 ([PyPI](https://pypi.org/project/mcdreforged/))，Prime Backup 提供遊戲內 `!!pb` 回檔。但 **itzg 映像檔不支援 MCDR**，社群做的混合映像只有 2 顆星、沒有測試 ([mcdr-docker](https://github.com/Cattttttttt/mcdr-docker))。改用官方 MCDR 映像的話，就得放棄 itzg 自動安裝 Fabric 和模組的功能。4–8 位朋友透過 Tailscale 連線的規模，直接用 port 區分各服就夠了，不需要 Velocity，也就不用處理 FabricProxy-Lite 和 modern forwarding ([FabricProxy-Lite](https://github.com/OKTW-Network/FabricProxy-Lite))。另外，目前沒有任何資料證實 Servux、Syncmatica 或 PCA 的自訂封包能在 26.x 穿過 Velocity 正常運作，省掉 Velocity 也就避開了這個未知數。

回滾分三層。Ledger 負責「某人誤拆了一段」這類局部回復。mc-backup 每 3 小時做一次整個世界的快照，處理機器炸掉、區塊損壞這類災難。創造鏡像服則讓玩家在上面試驗設計，主世界不用承擔風險。這樣的分層是常見做法，但目前沒有找到具名來源。

## 推薦方案與五種情境的替代路線

**主推薦：Fabric 26.3 原版伺服器**，伺服器端裝 Fabric API、Carpet、Carpet TIS Addition、Servux、Syncmatica、Lithium、FerriteCore、Ledger、Chunky；pca-protocol 可選。客戶端裝 Fabric Loader 0.20.1、MaLiLib、Litematica、MiniHUD、Tweakeroo、Item Scroller、Syncmatica。這個組合在 26.3 每一個元件都有正式版，V3、NBT 存檔、MiniHUD 伺服器資料和投影共享全部可用，原版行為以 vanilla 為基準。

| 情境 | 建議 | 代價／注意事項 |
|---|---|---|
| 一定要 Bukkit 插件生態 | 先用 Fabric 的 Ledger、LuckPerms、BlueMap、Chunky 滿足需求。真的非 Paper 不可，就等 Paper Accurate Block Placement 或 VeryMcProto 出 26.3 版，再用 Paper 26.3 加 vanilla 指南設定 | 現在 Paper 26.3 上沒有可靠的 V3；CoreProtect 要用 Patreon v25；Paper 官方承認無法 100% 原版 |
| 想等 Leaves | 別等。先開 Fabric 服，世界存檔日後可以轉移。Leaves 出 26.x 時，在鏡像服上評估 | Leaves 沒有時程，要用 `TYPE=CUSTOM`；Lophine（Folia）不建議用在 12 核主機 |
| 留在 1.21.11 LTS | 只在社群依賴 Carpet Extra 的規則（自動合成台、發射器規則等）或 Leaves 時考慮。TIS 把 1.21.11 列為 LTS ([TIS EOL](https://carpet.tis.world/eol)) | 你現有的兩台 Paper 都是 26.3，玩家得多維護一個客戶端；1.21.11 的 Carpet Extra 版本本研究沒有核實 |
| 另開創造／鏡像服 | 開一台**同樣用 Fabric 加 Servux** 的鏡像服（25567），定期把生存世界同步過去 | Servux 貼上**本來就要求創造模式**，鏡像服正好讓 `pasteUsingServux` 帶 NBT 快速貼上；Pekora 的 Paper 創造服只能用 `/setblock` 指令貼 |
| 之後需要 Carpet Extra 規則 | 等 gnembon 出 26.3 版再加裝 | Servux 的 mixin 會蓋過 Carpet Extra，Auto 也會優先選 V3，所以兩者並存沒有衝突 |

**Printer 和 Axiom 屬於規則面的決定。** litematica-printer 3.2.3（26.3）是純客戶端模組，伺服器端裝了 Servux 就能放出正確朝向，但它沒有對付防作弊的「legit mode」([GitHub](https://github.com/sakura-ryoko/litematica-printer))。朋友服不裝防作弊，所以技術上沒有障礙，要不要允許由你們自己約定。

## 照著做的部署規劃

目錄沿用 Pekora 的慣例：`/mnt/catjj/jay/mcs/techsmp/`，UID/GID 1002，時區 Asia/Taipei。生存服用 **25566**，鏡像服用 **25567**，Pekora 維持 25565。停用中的 Paper 生存服如果要復活，請改到 25568。只想讓 tailnet 連得到的話，可以把 port 綁在 Tailscale IP 上，寫成 `"100.x.y.z:25566:25565"`。

```yaml
# /mnt/catjj/jay/mcs/techsmp/docker-compose.yml
services:
  mc:
    image: itzg/minecraft-server:latest   # Pekora 已用此 tag 跑 26.3，代表 Java 版本相容；穩定後可改釘選 release tag
    container_name: mc-techsmp
    restart: unless-stopped
    tty: true
    stdin_open: true
    ports:
      - "25566:25565"
    mem_limit: 13g
    environment:
      EULA: "TRUE"
      TZ: Asia/Taipei
      UID: 1002
      GID: 1002
      TYPE: FABRIC
      VERSION: "26.3"
      FABRIC_LOADER_VERSION: "0.20.1"
      MEMORY: 10G
      USE_AIKAR_FLAGS: "true"
      MOTD: "TechSMP 26.3 | Fabric + Carpet + Servux"
      MODE: survival
      DIFFICULTY: hard
      MAX_PLAYERS: 10
      VIEW_DISTANCE: 10
      SIMULATION_DISTANCE: 10          # 農場依此設計，定案後不要再改
      SPAWN_PROTECTION: 0
      ONLINE_MODE: "true"
      ENABLE_WHITELIST: "true"
      PAUSE_WHEN_EMPTY_SECONDS: "0"    # 關閉空服自動暫停，讓掛機農場持續運作（首次啟動後確認 log 中沒有 pausing 訊息）
      ENABLE_RCON: "true"
      RCON_PASSWORD: "${RCON_PASSWORD}"
      ENABLE_ROLLING_LOGS: "true"
      OPS: |
        <你的 Minecraft ID>
      MODRINTH_DOWNLOAD_DEPENDENCIES: required
      MODRINTH_PROJECTS: |
        fabric-api
        fabric-language-kotlin
        carpet
        carpet-tis-addition
        servux
        syncmatica
        lithium
        ferrite-core
        ledger
        chunky
        pca-protocol?
    volumes:
      - ./data:/data

  mirror:
    image: itzg/minecraft-server:latest
    container_name: mc-techsmp-mirror
    restart: unless-stopped
    tty: true
    stdin_open: true
    ports:
      - "25567:25565"
    mem_limit: 8g
    environment:
      EULA: "TRUE"
      TZ: Asia/Taipei
      UID: 1002
      GID: 1002
      TYPE: FABRIC
      VERSION: "26.3"
      FABRIC_LOADER_VERSION: "0.20.1"
      MEMORY: 6G
      MOTD: "TechSMP Mirror (creative)"
      MODE: creative
      FORCE_GAMEMODE: "true"
      ONLINE_MODE: "true"
      ENABLE_WHITELIST: "true"
      SPAWN_PROTECTION: 0
      VIEW_DISTANCE: 10
      SIMULATION_DISTANCE: 10
      MODRINTH_DOWNLOAD_DEPENDENCIES: required
      MODRINTH_PROJECTS: |
        fabric-api
        carpet
        carpet-tis-addition
        servux
        syncmatica
        lithium
        ferrite-core
    volumes:
      - ./mirror-data:/data

  backup:
    image: itzg/mc-backup
    container_name: mc-techsmp-backup
    restart: unless-stopped
    hostname: techsmp-backup
    depends_on: [mc]
    environment:
      TZ: Asia/Taipei
      RCON_HOST: mc
      RCON_PASSWORD: "${RCON_PASSWORD}"
      BACKUP_METHOD: tar
      TAR_COMPRESS_METHOD: zstd
      BACKUP_INTERVAL: "3h"
      INITIAL_DELAY: "5m"
      PRUNE_BACKUPS_DAYS: 14
    volumes:
      - ./data:/data:ro
      - ./backups:/backups
```

同目錄放一個 `.env`，內容是 `RCON_PASSWORD=<隨機長字串>`，權限設成 600。itzg 每次啟動都會依 `MODRINTH_PROJECTS` 抓最新的相容版本。開服穩定後，請到 Modrinth 查出各模組的 version ID，改寫成 `servux:<versionID>` 的格式釘死，避免重啟時被自動升級，導致客戶端和伺服器的版本對不上 ([itzg Modrinth 文件](https://docker-minecraft-server.readthedocs.io/en/latest/mods-and-plugins/modrinth/))。sakura-ryoko 的 repo 在九月的正式版之後還有新 commit ([litematica repo](https://api.github.com/repos/sakura-ryoko/litematica))，之後可能會出新的小版本。

首次啟動並生成世界後，依下表完成伺服器端設定。

| 步驟 | 動作 | 驗證方式 |
|---|---|---|
| 1 | `docker compose up -d mc backup`，看 `docker logs -f mc-techsmp` | log 中出現 Fabric、Carpet、Servux、Syncmatica 載入，最後出現 Done |
| 2 | `docker exec mc-techsmp rcon-cli whitelist add <ID>`，逐一加入玩家 | `whitelist list` |
| 3 | 編輯 `data/config/servux.json`（或用 `/servux set …` 加 `/servux save`，需要權限 4；指令語法請用 tab 補完確認）：`litematic_data` 的 `permission_level_paste` 和 `permission_level_tasks` 設為 2；`hud_data` 的 `seed_permission_level` 設為 0（讓大家看得到史萊姆區塊）；`entity_data` 的 `fix_allay_gathering` 設為 false；`permission_level_easy_place` 維持 0 | 非 OP 玩家能用 Easy Place，MiniHUD 史萊姆區塊顯示正確 |
| 4 | 視需要關掉 Lithium 的非原版項目：`data/config/lithium.properties` 加一行 `mixin.minimal_nonvanilla=false` | 重啟後 log 沒有錯誤 |
| 5 | Carpet 規則：`/carpet setDefault commandPlayer true`（或維持 `ops`）。**不要**開 `fastRedstoneDust`、`optimizedTNT` 這類偏離原版的規則 | `/carpet list` |
| 6 | 預生成區塊：`/chunky radius 3000`，接著 `/chunky start` | 完成後 TPS 正常 |
| 7 | 確認 mc-backup 第一份備份已產生：`ls backups/` | 有 `.tar.zst` 檔 |

鏡像服的同步用主機上的 cron 執行下面這支腳本，例如每天 05:00。腳本先停掉鏡像服，在生存服暫停存檔的情況下用 rsync 複製世界，再恢復兩邊：

```bash
#!/usr/bin/env bash
# /mnt/catjj/jay/mcs/techsmp/refresh-mirror.sh
set -euo pipefail
cd /mnt/catjj/jay/mcs/techsmp
docker compose stop mirror
docker exec mc-techsmp rcon-cli save-off
docker exec mc-techsmp rcon-cli "save-all flush"
rsync -a --delete data/world/ mirror-data/world/
docker exec mc-techsmp rcon-cli save-on
docker compose start mirror
```

客戶端的模組包建議用 Prism Launcher 或 Modrinth App 建一個 26.3 Fabric instance，打包成 `.mrpack` 發給玩家。以下版本都查自 [Modrinth API](https://api.modrinth.com/v2/project/litematica/version?game_versions=%5B%2226.3%22%5D)，查詢日期 2026-11-17。

| 類別 | 模組與版本 |
|---|---|
| 必裝 | Fabric Loader 0.20.1、Fabric API 0.166.2+26.3、MaLiLib 0.30.2、Litematica 0.29.1、MiniHUD 0.41.2、Tweakeroo 0.30.1、Item Scroller 0.33.1、Syncmatica 0.3.20 |
| 建議 | Jade 26.3.5 或 WTHIT 21.0.0、AppleSkin 3.0.10、Xaero's Minimap／World Map |
| 可選 | Sodium mc26.3-0.9.3-beta.5（**beta**）、Iris 1.11.7、TweakerMore v3.33.3-beta.1（beta）、litematica-printer 3.2.3 |
| 不需要 | Servux（只裝在伺服器端）、Carpet（客戶端可選） |

客戶端設定方面，Litematica 的 `easyPlaceMode` 要開，`easyPlaceProtocolVersion` 設 **Auto** 或直接設 **Version 3**。「Auto 是否需要先開 `entityDataSync` 才能偵測到 Servux」這點沒有查證，所以建議直接設 V3，並且同時開啟 `entityDataSync`，這樣存檔才會帶 NBT。MiniHUD 要開 `hudDataSync`。Litematica 0.29.0 修正了與 Sodium 的相容性，但作者提到搭配光影時「有材質問題」([Modrinth Litematica 26.3](https://api.modrinth.com/v2/project/litematica/version?game_versions=%5B%2226.3%22%5D))。投影顯示異常時，先關掉 Iris 光影再判斷問題來源。

開放玩家前，用一張測試投影做驗收：投影裡要有朝上和朝下的偵測器、倒置樓梯、雙箱、左右門軸的門、延遲 4 的中繼器、減法模式的比較器、斜坡和轉角鐵軌、橫放原木、16 向告示牌，在生存模式用 Easy Place 蓋完，**重新登入**確認沒有幽靈方塊、狀態全部正確。接著存一個裝滿物品的箱子成投影，確認物品有帶進去；再用 Syncmatica 分享，讓另一位玩家能載入；最後確認 MiniHUD 的結構框和史萊姆區塊都有顯示。如果驗收時發現 V3 失效，先確認客戶端協定設定，再看伺服器 log 中 Servux mixin 有沒有載入。

## Conclusion

這次比較的關鍵是：26.3 上「有沒有伺服器能解 V3」這個硬性條件，比效能或插件生態更能決定選擇。Easy Place 把資料塞在原版會拒收的點擊座標裡，所以能力完全取決於伺服器端有沒有 mixin 或 patch。目前只有 Servux 同時滿足「有 26.3 版本」和「持續維護」，Carpet Extra 和 Leaves 的落後也就讓 Paper 系在這個需求上暫時出局。這個結構反過來也是風險。Litematica、Servux、Syncmatica、MiniHUD、Tweakeroo、Printer 全部由 sakura-ryoko 一人維護，26.4 出來時，整條生電工具鏈的更新速度都取決於他。所以伺服器應該把版本釘在 26.3，整個生命週期都不追新版本。

還有幾點目前不知道，開服前請自行確認：26.1 到 26.3 有沒有原版機制變動影響經典機器（更新抑制、TNT 複製等），本研究沒有涵蓋；Lithium 和 TIS 在 26.3 是否有互相衝突的回報沒有查；Leaves 26.x 何時恢復也沒有任何訊號。比較實際的觀察點是：如果 Paper Accurate Block Placement 或 VeryMcProto 出了 26.3 版，Paper 加插件就重新成為「想要插件生態」時的選項，可以先在鏡像服上評估，不必動主世界。
