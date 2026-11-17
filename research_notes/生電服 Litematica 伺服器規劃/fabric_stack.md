# Fabric server-side mod stack for a Minecraft Java 26.3 technical-survival (生電) server, with Litematica survival building as the top priority

Method note: every version/date below was pulled on 2026-11-17 from the public Modrinth API (`https://api.modrinth.com/v2/project/<slug>/version`, and `?loaders=["fabric"]` filtered). Source code and docs came from raw GitHub branches, mostly the `26.3` branches. The GitHub REST API rate-limited this IP partway through, so GitHub *releases* pages were not enumerated. Modrinth and the repo source/config files are the evidence. CurseForge was not checked directly. Modrinth lists 26.3 as a release dated 2026-09-15; 26.4 snapshots run up to 26.4-snapshot-8 (2026-11-10) — [Modrinth game_version tag API](https://api.modrinth.com/v2/tag/game_version).

## 1. Fabric Loader / Fabric API status for 26.3

### Takeaway
The base platform is mature on 26.3. Fabric Loader 0.20.1 is the current stable loader for 26.3, and Fabric API 0.166.2+26.3 (release, 2026-11-11) is under active development.

### Cited Findings
- Fabric Meta for 26.3 lists loader 0.20.1 as `stable: true`. 0.20.0 and 0.19.5 are older and flagged non-stable — [Fabric Meta loader/26.3](https://meta.fabricmc.net/v2/versions/loader/26.3)
- Fabric installer latest stable is 1.1.2 — [Fabric Meta installer](https://meta.fabricmc.net/v2/versions/installer)
- Fabric API 26.3 builds: 0.166.2+26.3 (release, 2026-11-11), 0.166.0+26.3 (2026-11-09), 0.165.2+26.3 (2026-11-03). Fabric API also already ships builds for 26.4 snapshots — [Modrinth fabric-api versions](https://api.modrinth.com/v2/project/fabric-api/version) / [page](https://modrinth.com/mod/fabric-api/versions)
- Servux 0.12.2 was built against loader 0.19.5 and Fabric API 0.161.0+26.3, which suggests a modest minimum version — [servux 26.3 gradle.properties](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/gradle.properties)

### Inferences
- Running loader 0.20.1 with the latest 0.166.x Fabric API is the safe baseline. Every mod checked declares compatibility with the 26.3 line, and none required an older Fabric API.

### Gaps
- Fabric loader release dates were not retrieved (Meta does not include dates).

## 2. Carpet (gnembon), Carpet Extra, and Carpet addons on 26.3

### Takeaway
Carpet core 26.3 exists (release, 2026-09-18). **Carpet Extra has NO 26.3 build.** Its newest build is for 26.2, and its jar hard-pins `minecraft: 26.2.x`. That matters for Litematica because `accurateBlockPlacement` (Easy Place protocol **V2**) is a Carpet *Extra* rule, not a Carpet core rule. So on 26.3, Easy Place in survival multiplayer depends on **Servux's V3**. Most major addons have 26.3 builds: TIS Addition, AMS, Org, GCA, Crystal, REMS and IGNY, plus Fallen-Breath's pca-protocol fork, which provides the PCA sync protocol.

### Cited Findings
**Carpet core**
- Carpet `26.3` release published 2026-09-18 (changelog: "support for Minecraft 26.3"). Beta builds 26.3-beta-1/2/3 for snapshots were published the same day. Modrinth marks it server required, client optional — [Modrinth carpet versions](https://api.modrinth.com/v2/project/carpet/version) / [page](https://modrinth.com/mod/carpet/versions)
- Carpet core rules relevant to technical and Litematica play (from the official settings list):
  - `fillUpdates`: "fill/clone/setblock and structure blocks cause block updates" (default true). Litematica's command-based paste suggests `/carpet fillUpdates false` to avoid block updates when pasting.
  - `interactionUpdates`: "placing blocks cause block updates" (default true).
  - `commandPlayer`: /player bots (default `ops`).
  - `allowSpawningOfflinePlayers`.
  - `fastRedstoneDust`: lag optimisation that "also fixes some locational behaviours or vanilla redstone MC-11193", so it is NOT vanilla-parity.
  - `movableBlockEntities`, `flippinCactus`, `placementRotationFix`, `missingTools`, `optimizedTNT`, `lagFreeSpawning`, `antiCheatDisabled`.
  - `accurateBlockPlacement` is **absent** from the core list.
  - Sources: [Carpet wiki Current-Available-Settings](https://raw.githubusercontent.com/wiki/gnembon/fabric-carpet/Current-Available-Settings.md) ([wiki page](https://github.com/gnembon/fabric-carpet/wiki/Current-Available-Settings)); [Litematica 26.3 lang (commandUseWorldEdit comment)](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)

**Carpet Extra (NOT on 26.3)**
- Modrinth: latest Carpet Extra builds are `26.2` (2026-06-21, game version 26.2) and `26.1` (2026-06-21). There is no 26.3 file — [Modrinth carpet-extra versions](https://api.modrinth.com/v2/project/carpet-extra/version) / [page](https://modrinth.com/mod/carpet-extra/versions)
- The fabric.mod.json inside `carpet-extra-26.2-26.2.jar` declares `"minecraft": "26.2.x"` and `"carpet": ">=26.2"`, so Fabric Loader will refuse to load it on 26.3 — [jar download](https://cdn.modrinth.com/data/VX3TgwQh/versions/Z5BJRYil/carpet-extra-26.2-26.2.jar)
- The repo `master` branch gradle.properties still says `minecraft_version=26.2` and `mod_version = 26.2` (checked 2026-11-17) — [carpet-extra master gradle.properties](https://raw.githubusercontent.com/gnembon/carpet-extra/master/gradle.properties)
- `accurateBlockPlacement` is documented as a Carpet Extra rule: "Client can provide alternative block placement", default false, categories EXTRAS, SURVIVAL — [carpet-extra README](https://raw.githubusercontent.com/gnembon/carpet-extra/master/README.md)
- Litematica's own help text: "Version 2: Compatible with servers with the Carpet mod (either QuickCarpet ... or CarpetExtra in addition to FabricCarpet. And in both cases the 'accurateBlockPlacement' Carpet rule needs to be enabled on the server)" — [Litematica 26.3 en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)

**Carpet TIS Addition (Fallen-Breath / TISUnion)**
- v1.83.3-mc26.3 (release, 2026-11-14). Earlier: v1.83.2-mc26.3 (2026-11-07) and v1.83.1-mc26.3 (2026-11-02). It already has 26.4-snapshot builds and is very actively maintained — [Modrinth carpet-tis-addition versions](https://api.modrinth.com/v2/project/carpet-tis-addition/version) / [page](https://modrinth.com/mod/carpet-tis-addition/versions)
- README: "Under the default configuration, this mod does not alter any vanilla behavior". Docs are at carpet.tis.world — [TIS README](https://raw.githubusercontent.com/TISUnion/Carpet-TIS-Addition/master/README.md); [docs](https://carpet.tis.world/docs)

**PCA protocol (plusls-carpet-addition and forks)**
- The original `plusls/plusls-carpet-addition` "stopped update in 2022", and the `Nyan-Work` fork "stopped in 2024". Fallen-Breath's **pca-protocol** is "a fork of plusls-carpet-addition, provides PCA protocol support to the server only". It "strips all of other features that might affect the vanilla game" and needs only Fabric Loader. It conflicts with the original PCA mod — [Modrinth pca-protocol](https://modrinth.com/mod/pca-protocol); [GitHub](https://github.com/Fallen-Breath/pca-protocol)
- pca-protocol v0.3.15-mc26.3 (release, 2026-09-19). Builds also exist for 26.2 and 26.1.x — [Modrinth pca-protocol versions](https://api.modrinth.com/v2/project/pca-protocol/version)
- Note: the Modrinth slug `pca` is an unrelated client mod ("Personal Compass Assistant", 1.21.x only) — [Modrinth pca](https://api.modrinth.com/v2/project/pca)
- Client consumers of PCA sync: MasaGadget (plusls) has no 26.x build on Modrinth; its latest Fabric files are v4.0.395 (2025-04-27, up to 1.21.3) — [Modrinth masa-gadget versions](https://api.modrinth.com/v2/project/masa-gadget/version). TweakerMore (Fallen-Breath) has v3.33.3-beta.1-mc26.3 (**beta**, 2026-09-26) — [Modrinth tweakermore versions](https://api.modrinth.com/v2/project/tweakermore/version)

**Other addons (all have Fabric 26.3 builds)**
- Carpet AMS Addition: mc26.3-v26.4-beta.4. Modrinth marks the file type "release" even though the version string says beta. Published 2026-11-07. Docs: https://carpet.mcams.club — [Modrinth versions](https://api.modrinth.com/v2/project/carpet-ams-addition/version); [GitHub](https://github.com/Minecraft-AMS/Carpet-AMS-Addition)
- Carpet Org Addition: 1.46.0 (release, 2026-09-16, 26.3). Self-description: "does not change the mechanics of any game by default, and all features need to be turned on manually". Features include villagerInfiniteTrade and commandPlayerAction for fake players — [Modrinth versions](https://api.modrinth.com/v2/project/carpet-org-addition/version); [page](https://modrinth.com/mod/carpet-org-addition)
- GCA (Gugle Carpet Addition, slug `gca`): v2.12.10+build.105 (release, 2026-10-25). One jar covers 26.1.1 through 26.3 and 26.4-snapshot-5 — [Modrinth gca versions](https://api.modrinth.com/v2/project/gca/version); [GitHub](https://github.com/Gu-ZT/gugle-carpet-addition)
- Crystal Carpet Addition: 1.15.0+mc26.3 (2026-09-16) — [Modrinth](https://api.modrinth.com/v2/project/crystalcarpetaddition/version)
- REMS-Carpet-Addition: 1.3.35 for 26.3 (2026-10-17) — [Modrinth](https://api.modrinth.com/v2/project/rems-carpet-addition/version)
- Carpet IGNY Addition: v1.21.1-mc26.3 (2026-10-16) — [Modrinth](https://api.modrinth.com/v2/project/carpet-igny-addition/version)

### Inferences
- On 26.3 you **cannot** get Easy Place V2 through Carpet + Carpet Extra. Servux (V3) is the required route for survival Easy Place. Note that Carpet alone sends the `carpet:hello` packet; see section 3 for why Litematica's Auto mode still picks V3 when Servux is present.
- If the community relies on Carpet Extra rules beyond accurateBlockPlacement, those are unavailable on 26.3 until gnembon ships an update. Examples include dispenser/renewable rules and `autoCraftingTable`, which are Carpet Extra features (not verified one by one here). This is the main "missing mod" on 26.x.
- PCA sync support for clients is available server-side via pca-protocol. However, the main PCA-consuming client mod (MasaGadget) is stale. On 26.x, Servux's entity_data provider is the main data-sync path for Litematica/MiniHUD/Tweakeroo.

### Gaps
- No public statement found from gnembon on Carpet Extra 26.3 timing. A CurseForge upload, a jitpack build or a GitHub Actions artifact for 26.3 might exist and was not checked (GitHub API rate-limited).
- I did not individually check which TIS/AMS/Org rules interact with Litematica, e.g., any rule replicating accurateBlockPlacement. Worth checking https://carpet.tis.world/docs and https://carpet.mcams.club.

## 3. Servux: exact server-side features (26.3 build 0.12.2)

### Takeaway
Servux 0.12.2 (release, 2026-09-27, 26.3) is now far more than "MiniHUD structure boxes". It has data providers for structures, HUD data, entities (NBT sync), Litematics (server-side paste and tasks), Tweaks (Tweakeroo), Scroller (Item Scroller mass craft) and debug data. It also does server-side **Easy Place protocol V3** handling with a validator. Litematica's Auto protocol selects **V3 whenever a Servux server is detected**. The Modrinth and README descriptions are outdated ("0.1.x only has one feature"). Source code is the authority.

### Cited Findings
- Versions: 0.12.2 (2026-09-27, changelog "add: paste_always_use_persistent"), 0.12.1 (2026-09-22, "fix permissions node syntax with sanitizer"), 0.12.0 (2026-09-21, "26.3"). All are release, Fabric only, server required, client unsupported — [Modrinth servux versions](https://api.modrinth.com/v2/project/servux/version) / [page](https://modrinth.com/mod/servux/versions)
- The Modrinth body and GitHub README still say "In version 0.1.x it only has one feature ... structure bounding box data to MiniHUD". This is stale — [Modrinth servux](https://api.modrinth.com/v2/project/servux); [README 26.3 branch](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/README.md)
- Data provider classes in the 26.3 branch: `StructureDataProvider`, `HudDataProvider`, `EntitiesDataProvider`, `LitematicsDataProvider`, `TweaksDataProvider`, `ServuxConfigProvider`, plus a Scroller provider and debug_data visible in config keys — [servux 26.3 dataproviders dir](https://github.com/sakura-ryoko/servux/tree/26.3/src/main/java/fi/dy/masa/servux/dataproviders); [servux 26.3 en_us.json](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/resources/assets/servux/lang/en_us.json)
- **Easy Place (servux_main):**
  - `permission_level_easy_place` (default 0): "The permission level required for the Easy Place operation".
  - `easy_place_validator_enabled` (default true): "Enable the Easy Place block state result validation".
  - Sources: [ServuxConfigProvider.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/dataproviders/ServuxConfigProvider.java); [en_us.json](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/resources/assets/servux/lang/en_us.json)
- **Litematica protocol selection (client side):**
  - "Version 3: Only supported by Litematica itself (in single player) or with Servux." — [Litematica 26.3 en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)
  - In `PlacementHandler.getEffectiveProtocolVersion()`, AUTO returns V3 if `isLocalServer()`, `EntityDataManager.hasServuxServer()` or `DataManager.hasServuxServer()`. So Servux takes precedence over the Carpet-based V2 fallback — [PlacementHandler.java (26.3)](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/util/PlacementHandler.java)
  - Litematica option `itemUsePacketCheckBypass`: bypasses the 1.18.2+ distance/coordinate check that otherwise turns rotated accurate-placement blocks into ghost blocks ("There is basically no need to ever disable this") — [Litematica en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)
- **entity_data provider (entity and block-entity NBT sync, e.g. for saving schematics with NBT in MP):**
  - Litematica `entityDataSync`: "Use the Entity Data Sync protocol from Servux to obtain Entity Data from the server". `entityDataSyncBackup` falls back to vanilla NBT Query, which "requires Operator Privileges". The block info overlay and `renderInfoOverlay` also need entityDataSync via Servux.
  - Servux settings: `permission_level` 0; `nbt_query_override` false; `nbt_query_permission_level` 2; `nbt_allow_player_inventory` true / `nbt_allow_player_ender_items` true (each gated at permission level 2).
  - **`fix_allay_gathering` default true**: "Fix Allay Gathering when 'mobGriefing' is disabled". This is a non-vanilla gameplay change that is enabled by default.
  - Sources: [EntitiesDataProvider.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/dataproviders/EntitiesDataProvider.java); [Litematica en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)
- **litematic_data provider (server-side paste):**
  - Litematica `pasteUsingServux`: "Use Servux to paste a schematic directly to the server. This method is much faster than the traditional command-based method, and it supports restoring Entity NBT Data. NOTE: requires entityDataSync". Error strings include "placement is too large to be safely transmitted to Servux".
  - Servux settings: `permission_level` 0, `permission_level_paste` **0**, `permission_level_tasks` 0, `fix_rail_rotations` / `fix_stairs_mirror` / `fix_chest_mirror` true, `deduplicate_schematic_entities` false, `paste_always_use_persistent` false (makes pasted leaves persistent).
  - Sources: [LitematicsDataProvider.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/dataproviders/LitematicsDataProvider.java); [Litematica en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)
- **structure_bounding_boxes provider:** sends MiniHUD structure boxes. It has a whitelist/blacklist, timeout and update interval, and optional seed and weather sharing with permission levels — [servux en_us.json](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/resources/assets/servux/lang/en_us.json)
- **hud_data provider (MiniHUD):**
  - `share_seed` (for the slime chunk display), `seed_permission_level`, `share_weather_status`, `weather_permission_level`.
  - `loggers_enabled` / `loggers_enable_list`: "Data Loggers, such as for TPS, and Mob Caps", with `logger_permission_level`.
  - Spawn-chunk-specific data was not seen in the config keys.
  - Source: [servux en_us.json](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/resources/assets/servux/lang/en_us.json)
- **tweaks_data provider (Tweakeroo):**
  - `stackable_shulkers` default **false**, `stackable_shulkers_count` 64. `stackable_shulkers_fix` default true ("prevent empty shulkers from stacking inside Hoppers (by KikuGie)").
  - Syncs config to Tweakeroo every `update_interval` ticks.
  - No hopper-lock feature was found in the config.
  - Source: [TweaksDataProvider.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/dataproviders/TweaksDataProvider.java)
- **scroller_data provider (Item Scroller):** `mass_craft_permission_level` — [servux en_us.json](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/resources/assets/servux/lang/en_us.json)
- Client mods on 26.3 (same day as Servux 0.12.2): Litematica 0.29.1, MiniHUD 0.41.2, Tweakeroo 0.30.1, MaLiLib 0.30.2 (all release, 2026-09-27). Litematica Printer (sakura-ryoko fork) 3.2.3 (2026-09-27) — [litematica](https://api.modrinth.com/v2/project/litematica/version), [minihud](https://api.modrinth.com/v2/project/minihud/version), [tweakeroo](https://api.modrinth.com/v2/project/tweakeroo/version), [malilib](https://api.modrinth.com/v2/project/malilib/version), [litematica-printer](https://api.modrinth.com/v2/project/litematica-printer/version)
- Related 26.3 helpers:
  - Fallen-Breath's **Litematica Server Paster** ("Let Litematica be able to paste tile entity data of block / entity data in a server"): v1.3.14-mc26.3, 2026-09-26 — [Modrinth](https://api.modrinth.com/v2/project/litematica-server-paster/version)
  - Client-side Easy Place orientation fixers: EasyPlaceFix fork 0.6.7 (26.3, 2026-10-05) — [Modrinth](https://api.modrinth.com/v2/project/easyplacefix-fork/version); EasyPlaceFixPlus 1.0.22+26.3 (2026-10-26) — [Modrinth](https://api.modrinth.com/v2/project/easyplacefixplus/version)

### Inferences
- For the stated top priority (survival Easy Place V3), Servux 0.12.2 on the server is the only required server-side piece. Clients can leave the protocol on Auto or set "Version 3" explicitly.
- **Admin hardening:** paste, tasks, and Easy Place all default to permission level 0. Any player with Litematica could server-paste schematics (creative-like injection) unless `permission_level_paste` and `permission_level_tasks` are raised, e.g. to 2 or higher. For survival integrity this should be changed. The default player inventory/ender-item NBT sharing is level 2, i.e. ops only.
- To keep vanilla parity, consider setting `fix_allay_gathering` to false. It is default true, but only matters when mobGriefing=false.

### Gaps
- The exact server-side validation behaviour of `easy_place_validator_enabled` (which states it rejects) was not read from source.
- The Servux config file path and command syntax (`/servux ...`) were not verified. The lang file shows `servux.command.config.list.data_provider`, which implies a config command exists.

## 4. Syncmatica (shared placements) and alternatives on 26.x

### Takeaway
Syncmatica has a 26.3 build, 0.3.20 (release, 2026-09-22), now maintained by sakura-ryoko. A feature-rich Chinese-community fork, **Syncmatica Revolution** (Conflux-Union / RMS-Server), has v0.5.5-mc26.3 (2026-11-14). It adds shared material-progress tracking.

### Cited Findings
- Syncmatica 0.3.20 for 26.3 (release, 2026-09-22). Source: github.com/sakura-ryoko/syncmatica. Credits: original by nnnik, 1.20 port by kpzip, "Newer ports by sakura-ryoko". Required on server and on any client that wants to use it. Warning: "gives its users a lot of power and can have consequences for the server" — [Modrinth syncmatica](https://modrinth.com/mod/syncmatica); [versions API](https://api.modrinth.com/v2/project/syncmatica/version)
- Syncmatica Revolution: v0.5.5-mc26.3 / mc26.2 / mc26.1 (release, 2026-11-14). It is a "modified fork of Syncmatica (End-Tech)" adding "Shared Material Progress Tracking": server-scanned material requirements, a claim system, stocking-area container scans and a live HUD overlay — [Modrinth syncmatica-revolution](https://modrinth.com/mod/syncmatica-revolution); [versions API](https://api.modrinth.com/v2/project/syncmatica-revolution/version); [GitHub](https://github.com/Conflux-Union/syncmatica_r)
- Syncmatica Paper (server-side for Paper/Purpur/Folia) exists. It is not relevant on Fabric, but notable if a Paper path is considered — [Modrinth syncmatica-paper](https://modrinth.com/mod/syncmatica-paper)
- LitematicaSync (client only, 1.0.1 for 26.3, 2026-10-11) "Synchronizes Litematica placements and configurations across different server IPs". This is not player-to-player sharing — [Modrinth litematicasync](https://api.modrinth.com/v2/project/litematicasync/version)

### Inferences
- Syncmatica and Syncmatica Revolution are probably mutually exclusive, since both are forks of the same mod and likely share the protocol and IDs. Pick one per server; clients need the matching mod.

### Gaps
- Not verified whether Syncmatica Revolution clients interoperate with stock Syncmatica servers, or whether either conflicts with Servux.
- No info found on whether Litematica itself has gained built-in placement sharing.

## 5. Performance mods and vanilla parity (26.3 status)

### Takeaway
Lithium (26.3, 0.26.3), FerriteCore, Krypton, C2ME (**alpha**) and ScalableLux (**alpha**) all have Fabric 26.3 builds. Upstream ModernFix has **no** Fabric 26.x build; only the ModernFix-mVUS fork does. Noisium is dead (1.21.6), and its fork NoisiumForked stops at 26.2. Starlight is abandoned; ScalableLux is its successor. Lithium explicitly documents its few "minimal_nonvanilla" deviations, and all of them can be turned off.

### Cited Findings
**Lithium**
- 26.3 Fabric builds: mc26.3-0.26.3-fabric (release, 2026-10-28), 0.26.2 (2026-09-28), 0.26.1 (2026-09-16). The 0.26.1 changelog says: "Disable optimization that causes chunk corruption". The 0.26.3 fixes include "Avoid caching chest inventories when the corresponding block state is a chest half" — [Modrinth lithium versions (fabric)](https://api.modrinth.com/v2/project/lithium/version?loaders=%5B%22fabric%22%5D)
- Policy: "with the goal of **not changing any vanilla mechanics** ... The strict goal of maintaining exact behavior with vanilla makes Lithium suitable for almost any Minecraft server ... even for highly complex gameplay scenarios and creations". It is officially allowed in speedrunning — [Modrinth lithium](https://modrinth.com/mod/lithium)
- Wiki: "minimally invasive optimizations which do not change vanilla behaviour (except where such behaviour would otherwise be undefined.)" — [Lithium wiki Home](https://github.com/CaffeineMC/lithium-fabric/wiki)
- **Documented exceptions**, the `mixin.minimal_nonvanilla.*` options (all default true), described as "technically deviate from vanilla behavior, but must not affect gameplay or contraptions ... In case any of these optimizations breaks any of your contraptions ... we consider this to be a bug":
  - `ai.sensor.frog_attackables`: frog visibility caching differences.
  - `collisions.empty_space`: entity placement differences within 1e-7 blocks for nether portals and pose changes.
  - `spawning`: floating-point summation order for density-controlled spawns, e.g. skeleton, ghast, enderman and strider in certain nether biomes.
  - `world.block_entity_ticking.support_cache`: placing a hopper in a powered location immediately updates the cached BlockState; "In vanilla, hoppers never use this cached state information anyway".
  - `world.expiring_chunk_tickets`: "Can cause reordering of chunks unloading ... No known contraptions depend on the unload order".
  - Source: [lithium-fabric-mixin-config.md @ mc26.3-0.26.3](https://raw.githubusercontent.com/CaffeineMC/lithium/mc26.3-0.26.3/lithium-fabric-mixin-config.md)
- Other relevant options: `mixin.block.hopper` (default true, "Reduces hopper lag using caching, notification systems and BlockEntity sleeping") and `mixin.block.redstone_wire` ("avoid duplicate block accesses") — [same file](https://raw.githubusercontent.com/CaffeineMC/lithium/mc26.3-0.26.3/lithium-fabric-mixin-config.md)
- Past hopper-related bug fixes appear in the changelogs, e.g. hoppers not noticing direction changes in mc1.17.1-0.7.4. This shows caching bugs can and do occur — [newreleases mc1.17.1-0.7.4](https://newreleases.io/project/github/CaffeineMC/lithium-fabric/release/mc1.17.1-0.7.4); [Lithium releases](https://github.com/CaffeineMC/lithium-fabric/releases)

**C2ME (Concurrent Chunk Management Engine)**
- 26.3: 0.4.2-alpha.0.119+26.3 (**alpha**, 2026-11-12); it ships very frequent alpha builds — [Modrinth c2me-fabric versions](https://api.modrinth.com/v2/project/c2me-fabric/version)
- "C2ME does not sacrifice vanilla functionality or behavior, or alter the vanilla world generation in the name of raw speed by default." However, "due to the non-determinism of vanilla world generation (MC-55596), worlds will vary significantly run-to-run even with the same seed". Recommended with Lithium and ScalableLux — [Modrinth c2me-fabric](https://modrinth.com/mod/c2me-fabric)

**ScalableLux (Starlight successor)**
- 26.3 Fabric: 0.3.0-alpha.0.6+26.3 (**alpha**, 2026-09-16) — [Modrinth scalablelux versions](https://api.modrinth.com/v2/project/scalablelux/version)
- "A Fabric mod based on Starlight that improves the performance of light updates"; "Starlight is no longer maintained as a mod since Mar 8, 2024"; it "optionally allows for parallel light updates" — [Modrinth scalablelux](https://modrinth.com/mod/scalablelux)
- Starlight (Fabric): last build 1.1.3+1.20.4 (2023-12-10) — [Modrinth starlight versions](https://api.modrinth.com/v2/project/starlight/version)

**FerriteCore**
- 9.0.0-fabric (release, 2026-03-24). One jar declared for 26.1 through 26.3 — [Modrinth ferrite-core versions](https://api.modrinth.com/v2/project/ferrite-core/version)

**Krypton (networking)**
- 0.3.2 for 26.3 (release, 2026-09-30). The author warns: "I do not provide any guarantees about Krypton's stability, compatibility with other mods ... Support ... best-effort" — [Modrinth krypton](https://modrinth.com/mod/krypton); [versions](https://api.modrinth.com/v2/project/krypton/version)

**ModernFix**
- The upstream ModernFix Modrinth project's 26.x files are **NeoForge only**: 5.27.27+mc26.1.2 (2026-11-06), with no 26.3. The latest upstream Fabric file is 5.25.2+mc1.20.1 (2025-12-08) — [Modrinth modernfix versions](https://api.modrinth.com/v2/project/modernfix/version)
- The ModernFix-mVUS fork ("adds minor version update support") has a Fabric 5.27.20-build.2 for 26.3 (release, 2026-09-25) and a NeoForge 5.27.23+mc26.3 — [Modrinth modernfix-mvus versions](https://api.modrinth.com/v2/project/modernfix-mvus/version)

**Noisium**
- Original: last build 2.7.0+mc1.21.6 (2025-06-24) — [Modrinth noisium](https://api.modrinth.com/v2/project/noisium/version). NoisiumForked: latest 2.8.5+mc26.2 (2026-05-30), **no 26.3** — [Modrinth noisiumforked](https://api.modrinth.com/v2/project/noisiumforked/version)

### Inferences
- **Conservative 生電 baseline:** Lithium (release, explicit parity policy; consider disabling `mixin.minimal_nonvanilla` if paranoid about spawn-rate or chunk-unload-order experiments) plus FerriteCore (memory only). For a stable stack, Krypton is probably fine (network only), but its maintenance is best-effort.
- C2ME and ScalableLux are alpha on 26.3. Both touch chunk loading and lighting, which are areas technical players probe (chunk loading and unloading behaviour, light-update mechanics). Treat them as opt-in and test with your farms first. This caution is my inference; no source found documenting specific contraption breakage.
- Skip Noisium and Starlight entirely on 26.3, and skip upstream ModernFix on Fabric.

### Gaps
- **No authoritative community (Chinese 生電 or TMC) source found** stating which performance mods are "approved". Web searches returned only generic hosting guides. The view that "Lithium is fine for technical play and Starlight-style light engines are risky for light-suppression contraptions" is common community lore but **unverified here**. ScalableLux docs do not mention light suppression.
- No 26.3-specific Lithium vs. Carpet TIS incompatibility reports were checked; the issue trackers were not searched.

## 6. Server management / admin mods on Fabric 26.3

### Takeaway
Ledger, LuckPerms (Fabric), fabric-permissions-api, Chunky, squaremap and BlueMap all have 26.3 Fabric builds. **Textile Backup has no 26.x build** (last: 1.21.x, 2024), and neither does X Backup (last: 1.21.11). The available 26.3 backup options are smaller mods such as "Simple Backups for Fabric" (unofficial port), or external scripting.

### Cited Findings
- **Ledger** (QuiltServerTools, CoreProtect-like logging and rollback): 1.3.25 (release, 2026-10-04, loaders fabric and quilt, 26.3). 1.3.24 was released 2026-09-19. It requires Fabric Language Kotlin, per the badge in the description — [Modrinth ledger versions](https://api.modrinth.com/v2/project/ledger/version); [page](https://modrinth.com/mod/ledger); [GitHub](https://github.com/QuiltServerTools/Ledger)
- **LuckPerms**: v5.5.85-fabric (release, 2026-09-19), declared for 26.1 through 26.3. A newer v5.5.87 exists only for NeoForge (2026-10-06) — [Modrinth luckperms versions](https://api.modrinth.com/v2/project/luckperms/version)
- **fabric-permissions-api**: 0.7.0 (release, 2026-05-27), declared for 26.1 through 26.3 — [Modrinth versions](https://api.modrinth.com/v2/project/fabric-permissions-api/version)
- **Chunky** (pre-generation): 1.5.66 (release, 2026-11-04), Fabric, 26.1 through 26.3 — [Modrinth chunky versions](https://api.modrinth.com/v2/project/chunky/version)
- **squaremap**: 1.4.3 Fabric for 26.3 (release, 2026-10-16) — [Modrinth squaremap versions](https://api.modrinth.com/v2/project/squaremap/version)
- **BlueMap**: 5.29-fabric (release, 2026-10-10), 26.1 through 26.3 — [Modrinth bluemap versions (fabric)](https://api.modrinth.com/v2/project/bluemap/version?loaders=%5B%22fabric%22%5D)
- **Textile Backup**: latest 3.1.3-1.21 (2024-06-26, up to 1.21.9). **No 26.x** — [Modrinth textile_backup versions](https://api.modrinth.com/v2/project/textile_backup/version)
- **X Backup** (zly2006): latest 0.3.16+1.21.11 (2026-01-12). **No 26.x** — [Modrinth x-backup versions](https://api.modrinth.com/v2/project/x-backup/version)
- **Simple Backups for Fabric** ("An unofficial Fabric port of SimpleBackups"): 26.3.0 (2026-09-30) and 26.3.0-gui (2026-10-08) — [Modrinth versions](https://api.modrinth.com/v2/project/simple-backups-for-fabric/version)
- A "FabricBackup" slug does not exist on Modrinth (404). Search also surfaced `simple-server-backups` and `simple-backups` with 26.3 tags, not examined in detail — [Modrinth search "simple backups"](https://api.modrinth.com/v2/search?query=simple%20backups)

### Inferences
- The admin side is well covered on 26.3. For backups, a host-level snapshot or rsync script while the save is paused (`save-off`/`save-all`) may be more robust than relying on a small, recently ported mod. This is a design suggestion, not a sourced fact.

### Gaps
- Fabric Language Kotlin's 26.3 availability (needed by Ledger) was not explicitly queried, though Ledger publishing a 26.3 build implies it exists.

## 7. Breakage or missing mods on 26.x that might keep a technical server on an older version

### Takeaway
The only significant hole found for a Litematica-first 生電 server on 26.3 is **Carpet Extra** (no 26.3 build). Its absence removes `accurateBlockPlacement`/V2, but Servux V3 fully replaces that for Easy Place. Smaller gaps: MasaGadget is stale, C2ME and ScalableLux are alpha-only, upstream ModernFix has no Fabric build, and Textile Backup and X Backup have no 26.x builds. Everything else in the core technical stack has 26.3 builds dated September to November 2026: Carpet, TIS, AMS, Org, GCA, pca-protocol, Servux, Syncmatica, Lithium, Ledger, LuckPerms, Chunky and the maps.

### Cited Findings
- Carpet Extra: last builds 26.2 and 26.1, jar pinned to `minecraft 26.2.x` — [Modrinth carpet-extra](https://api.modrinth.com/v2/project/carpet-extra/version); [master gradle.properties](https://raw.githubusercontent.com/gnembon/carpet-extra/master/gradle.properties)
- MasaGadget: no 26.x — [Modrinth masa-gadget](https://api.modrinth.com/v2/project/masa-gadget/version)
- TweakerMore 26.3 is beta only (v3.33.3-beta.1-mc26.3) — [Modrinth tweakermore](https://api.modrinth.com/v2/project/tweakermore/version)
- C2ME (0.4.2-alpha...+26.3) and ScalableLux (0.3.0-alpha...+26.3) are alpha — [c2me](https://api.modrinth.com/v2/project/c2me-fabric/version); [scalablelux](https://api.modrinth.com/v2/project/scalablelux/version)
- Textile Backup and X Backup have no 26.x builds — [textile_backup](https://api.modrinth.com/v2/project/textile_backup/version); [x-backup](https://api.modrinth.com/v2/project/x-backup/version)
- NoisiumForked tops out at 26.2 — [noisiumforked](https://api.modrinth.com/v2/project/noisiumforked/version)

### Inferences
- There is no compelling reason to stay on 1.21.x for a Litematica-first server, **unless** the community specifically depends on Carpet Extra rules other than accurateBlockPlacement, or on PCA-sync features via MasaGadget.
- 26.4 snapshots are already being targeted by Fabric API, TIS, AMS, GCA and C2ME. When 26.4 releases, expect another update lag, most acutely for Carpet Extra. Pinning to 26.3 for the server's life cycle is reasonable.

### Gaps
- No search was done for Mojang-side 26.x technical changes that break classic contraptions (e.g. update suppression, TNT duping, chunk-loading changes). That is outside this mod-stack scope and was not researched here.
- Carpet Extra's CurseForge page and any unofficial 26.3 ports were not checked.
