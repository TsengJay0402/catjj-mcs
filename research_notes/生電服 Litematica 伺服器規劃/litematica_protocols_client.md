# Litematica survival-building protocols and the client mod setup for Minecraft Java 26.3 (server-side requirements)

Research date: 2026-11-17. Primary sources: the source code of the `26.3` branches of sakura-ryoko's forks (these are the codebases published as the official Litematica, Servux, MiniHUD and Tweakeroo builds on Modrinth), the Modrinth v2 API (`/v2/project/<slug>/version?game_versions=["26.3"]`), and the Fabric meta API. Source files were read on raw.githubusercontent.com. GitHub's REST API hit its rate limit partway through, so the commit-history dates for when protocol code was introduced could not be pulled (see Gaps).

Key repos and branch facts:
- sakura-ryoko/litematica is a fork of maruohon/litematica. Its default branch is `26.3`, last pushed 2026-11-11. It also has LTS branches from 1.19.4 through 26.2. — [GitHub API repo](https://api.github.com/repos/sakura-ryoko/litematica), [branches](https://api.github.com/repos/sakura-ryoko/litematica/branches?per_page=100)
- maruohon/litematica (masa's own repo) has default branch `ornithe/1.12.2`. masa is not maintaining the modern Fabric versions. — [GitHub API](https://api.github.com/repos/maruohon/litematica)
- In the Servux 0.2.0 changelog (2024-06-13, MC 1.20.5/1.20.6) masa wrote: "This update is entirely the work of Sakura-Ryoko. I don't currently have any plans to update my mods anymore from the old 'pre-rewrite' code for any MC versions after 1.20.4." — [Modrinth Servux versions API](https://api.modrinth.com/v2/project/servux/version)
- The Modrinth "litematica" project (id bEpr0Arc) lists `source_url` = https://github.com/sakura-ryoko/litematica. So the official Modrinth Litematica *is* the sakura-ryoko build. — [Modrinth project API](https://api.modrinth.com/v2/project/litematica)

---

## 1. Easy Place mode and the `easyPlaceProtocolVersion` options (Auto / V3 / V2 / Slabs only / None)

### Takeaway
Easy Place encodes the target block state into the *hit vector X coordinate* of the vanilla "use item on block" packet: hitX = blockX + 2 + protocolValue. A plain vanilla or Paper server treats a hit X more than about 1 block from the block as invalid (a check added in 1.18.2), so any V2 or V3 placement there becomes a ghost block. Full-orientation placement in multiplayer on 26.3 therefore needs **Servux 0.12.2 (V3)** on a Fabric server. Leaves (built-in Servux-protocol emulation) may also work but is unverified. **Carpet Extra (V2) has no 26.3 build**, and with neither, Auto falls back to "Slabs only".

### Cited Findings
**Config definition (26.3 code)**
- The config key is `easyPlaceProtocolVersion` (Generic tab) and defaults to `AUTO`. The enum values and their serialized strings are `auto`, `v3`, `v2`, `slabs_only`, `none`, shown in the GUI as "Auto", "Version 3", "Version 2", "Slabs only", "None". — [Configs.java L47](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/config/Configs.java); [EasyPlaceProtocol.java](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/util/EasyPlaceProtocol.java)
- Official in-game tooltip text in 26.3 (en_us.json), verbatim:
  - "Auto: Uses v3 in single player, and by default Slabs-only in multiplayer, unless the server has Carpet mod that sends a 'carpet:hello' packet, in which case v2 is used on that server."
  - "Version 3: Only supported by Litematica itself (in single player) or with Servux."
  - "Version 2: Compatible with servers with the Carpet mod (either QuickCarpet by skyrising and DeadlyMC, or CarpetExtra in addition to FabricCarpet. And in both cases the 'accurateBlockPlacement' Carpet rule needs to be enabled on the server)."
  - "Slabs only: Only fixes top slabs. Compatible with Paper servers."
  - "None: Does not modify coordinates."
  — [lang/en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)
- **The actual Auto logic in code is newer than the tooltip.** `PlacementHandler.getEffectiveProtocolVersion()` returns V3 if `Minecraft.isLocalServer()`, or if `EntityDataManager.hasServuxServer()` or `DataManager.hasServuxServer()` is true. Otherwise it returns V2 if `DataManager.isCarpetServer()` (carpet:hello) is true, and otherwise SLAB_ONLY. Auto therefore picks V3 automatically when Servux is detected. — [PlacementHandler.java](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/util/PlacementHandler.java)
- A third-party guide dated 2026-10-31 agrees: "On Servux, Easy Place's Auto mode switches to Version 3", and otherwise Slabs-only or V2 on Carpet with `accurateBlockPlacement`. — [space-node.net blog](https://space-node.net/blog/litematica-multiplayer-server-syncmatica-servux-2026)

**V3 encoding (exact, from `applyPlacementProtocolV3`)**
- `protocolValue = (int)(hitVec.x - pos.getX()) - 2`. If it is less than 0, the state is left unchanged, so normal clicks (hitX within the block) are unaffected. — [PlacementHandler.java](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/util/PlacementHandler.java)
- Facing: the block's first Direction-type property (any except `VERTICAL_DIRECTION`, the pointed dripstone property) is decoded from `(protocolValue & 0xF) >> 1`, which is bits 1-3:
  - 0-5 = `Direction.from3DDataValue` (down, up, north, south, west, east).
  - 6 = the opposite of the normal placement facing.
  - If the requested facing is invalid for the property, it falls back to the player's opposite direction.
  - Beds check that the head position is replaceable.
  After the facing, 3 bits and then 1 more bit are consumed. — same source
- Other properties: all of the block's properties are sorted alphabetically by name. Each whitelisted property takes `log2(nextPowerOfTwo(numValues))` bits, and that index selects into the property's sorted value list. — same source
- The whitelist covers: INVERTED, OPEN, BELL_ATTACHMENT, AXIS, HALF, ATTACH_FACE, CHEST_TYPE, MODE_COMPARATOR, DOOR_HINGE, FACING, HORIZONTAL_FACING, FACING_HOPPER, ORIENTATION (crafter), RAIL_SHAPE, RAIL_SHAPE_STRAIGHT, SLAB_TYPE, STAIRS_SHAPE, COPPER_GOLEM_POSE, BITES (cake), DELAY (repeater), NOTE (note block), ROTATION_16 (banners, signs, skulls). PERSISTENT (leaves) is commented out. — same source
- Restrictions:
  - The blacklisted properties WATERLOGGED and POWERED are forced to false. WATERLOGGED is restored if the original position was water.
  - SlabType.DOUBLE is refused via the protocol ("don't allow duping slabs").
  - With `easyPlaceSinglePlayerValidation`, each step is checked with `canSurvive`.
  — same source

**V2 encoding (Carpet `accurateBlockPlacement`)**
- V2 computes the same `protocolValue`:
  - The direction comes from `(value & 0xF) >> 1`, or the axis from `((value >> 1) & 3) % 3`.
  - After `>>> 5`, a remaining value greater than 0 sets the repeater DELAY to that value and puts a comparator in SUBTRACT mode, and any HALF property becomes TOP when the value is greater than 0, otherwise BOTTOM.
  V2 therefore covers facing, axis, repeater delay, comparator mode and top/bottom half only. It does not cover chest type, door hinge, rail shape, note, rotation_16 and so on, which V3 adds. — [PlacementHandler.java](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/util/PlacementHandler.java)

**Why unsupported servers produce ghost blocks**
- Litematica config `itemUsePacketCheckBypass` (default true) carries this tooltip: "Bypass the new distance/coordinate check that was added in 1.18.2. That check breaks the 'accurate placement protocol' and causes any blocks placed with a rotation (or other property) request to just become ghost blocks." Its mixin wraps `Vec3.subtract` in `ServerGamePacketListenerImpl.handleUseItemOn` and returns `Vec3.ZERO`. This only affects the integrated (single-player/LAN) server running inside the client. — [en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json); [MixinServerGamePacketListenerImpl_easyPlace.java](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/mixin/easyplace/MixinServerGamePacketListenerImpl_easyPlace.java)
- Litematica wiki (last edited 2023-11-28): "you will get ghost blocks when you try to place any blocks that have a rotation property via the Easy Place mode" without server support, and "Do not keep the `easyPlaceProtocolVersion` config hard coded to `Version 2` or `Version 3` on servers that do not have CarpetExtra or Litemoretica mods." Carpet is detected "by tracking whether the 'carpet:hello' packet was sent." — [maruohon/litematica wiki: Easy Place](https://github.com/maruohon/litematica/wiki/Easy-Place)
- The same wiki page says V3 in multiplayer needs Litemoretica on server and client. The page predates Servux's V3 support. — [wiki](https://github.com/maruohon/litematica/wiki/Easy-Place)

**Servux's V3 implementation (26.3)**
- Servux has a `BlockItem#getPlacementState` mixin with priority 950, commented "Should override Carpet-Extra's version with a higher priority".
  - If the player lacks the Easy Place permission, it does nothing and vanilla behaviour applies.
  - Otherwise it computes the vanilla state. If `easy_place_validator_enabled` is off, or `canPlace` passes, it returns `PlacementHandler.applyPlacementProtocolV3(...)`.
  - Servux also ships `mixin/easy_place/MixinServerGamePacketListenerImpl_easyPlace.java` (the server-side counterpart of the hit-position check bypass).
  — [Servux MixinBlockItem_EasyPlace.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/mixin/easy_place/MixinBlockItem_EasyPlace.java); [Servux tree](https://github.com/sakura-ryoko/servux/tree/26.3/src/main/java/fi/dy/masa/servux/mixin/easy_place)
- Servux config keys (category `servux_main`):
  - `permission_level_easy_place`: "The permission level required for the Easy Place operation".
  - `easy_place_validator_enabled`: "Enable the Easy Place block state result validation".
  — [Servux en_us.json](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/resources/assets/servux/lang/en_us.json)
- Servux's permission checks go through vanilla 26.x `Entity.checkPermission(Identifier node, PermissionLevel)` with sanitized nodes such as `<provider>.data_provider`. Permission plugins and mods can therefore grant nodes, and op level is the fallback. — [Servux PermissionsUtil.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/util/PermissionsUtil.java)
- Per the 2026-10-31 guide, the Servux config lives in `config/servux.json` and `servux_main:permission_level_easy_place` defaults to 0 (all players). — [space-node.net](https://space-node.net/blog/litematica-multiplayer-server-syncmatica-servux-2026)

**V3 history**
- Search results quote a Servux changelog entry "Adds V3 Easy Place Protocol support for Litematica and Tweakeroo without requiring Carpet Extra", attributed to a Servux 0.3.0-rc1/0.3.7 page on Modrinth. That page now returns 404 and could not be re-verified. — [search lead: modrinth.com/mod/servux/version/0.3.7 (404 on fetch)](https://modrinth.com/mod/servux/version/0.3.7)
- Litematica 0.19.50 (2024-08-20, MC 1.21.1) has several Easy Place protocol fixes. Tweakeroo 0.21.50 (2024-08-20) "Fixes accuratePlacementProtocol V3 to avoid placing invalid block states (Such as Floating Buttons)". Litematica 0.20.2 (2024-12-22) has "fix: Easy Place V3 for AXIS BlockStates; meaning this fixes Logs, Froglights, Basalt, Hyphae". — [Modrinth Litematica versions API](https://api.modrinth.com/v2/project/litematica/version); [Tweakeroo versions API](https://api.modrinth.com/v2/project/tweakeroo/version)
- Litemoretica, the older third-party server and client mod for V3, has 1.2.5+mc1.21.1 (2024-09-20) as its newest build. There is **no 26.x build**. — [Modrinth litemoretica API](https://api.modrinth.com/v2/project/litemoretica/version)

**26.3 server-side availability**
- Servux 0.12.2 (2026-09-27, changelog "add: paste_always_use_persistent"), 0.12.1 (2026-09-22, "fix permissions node syntax with sanitizer") and 0.12.0 (2026-09-21) all target 26.3. — [Modrinth Servux 26.3 API](https://api.modrinth.com/v2/project/servux/version?game_versions=%5B%2226.3%22%5D)
- Carpet (fabric-carpet) "26.3" was released 2026-09-18 ("support for Minecraft 26.3"). — [Modrinth carpet 26.3 API](https://api.modrinth.com/v2/project/carpet/version?game_versions=%5B%2226.3%22%5D)
- **Carpet Extra has no 26.3 version.** The latest are "26.2" (2026-06-21) and "26.1" (2026-06-21). — [Modrinth carpet-extra API](https://api.modrinth.com/v2/project/carpet-extra/version)
- The Leaves (Paper fork) config reference has these protocol keys, all with default `false` in the sample: `settings.protocol.servux.structure-protocol`, `entity-protocol`, `hud-metadata-protocol` (plus `hud-metadata-protocol-share-seed: true`), `litematics-protocol`, `leaves-carpet-support`, `jade-protocol`, `bbor-protocol`, `xaero-map-protocol`, and `alternative-block-placement: NONE`. Also present are `settings.protocol.syncmatica.enable/quota/quota-limit: 40000000`, `settings.protocol.pca.pca-sync-protocol`, and `settings.minecraft-old.disable-distance-check-for-use-item: false`. Indentation was flattened in the fetched page, so the parent paths are inferred. — [Leaves docs: configuration](https://docs.leavesmc.org/leaves/reference/configuration)
- Paper-side plugin "paper-accurate-block-placement" ("implementation of the accurate block protocol and flexible block protocol for paper/purpur") lists 26.1.2/26.2 as its newest versions (modified 2026-08-21), with **no 26.3** at search time. — [Modrinth search API](https://api.modrinth.com/v2/search?query=accurate%20block%20placement&limit=8)

**Other Easy Place configs (26.3)**
- `easyPlaceVanillaReach`: "reduces reach distance from +1.0 to the Vanilla value so servers don't reject placement of far blocks". — [en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)
- `easyPlaceSwapInterval`: "Useful to avoid placing wrong blocks when having high ping". — same source
- Also present: `easyPlaceHoldEnabled`, `easyPlaceFirst`, and `easyPlacePostRewrite` ("uses the 'Post-Rewrite' code from 1.12.2 ornithe. WARNING! THIS IS EXPERIMENTAL"). — same source
- Litematica 0.29.1 (2026-09-27) changelog: "fix a few edge cases of invalid Easy Place clicks." — [Modrinth Litematica 26.3 API](https://api.modrinth.com/v2/project/litematica/version?game_versions=%5B%2226.3%22%5D)

### Inferences
- On a vanilla or Paper 26.3 server, Auto resolves to "Slabs only".
  - Slabs only adjusts the hit Y inside the block, which is legal, so top slabs come out right.
  - Every other property comes from vanilla placement logic: player look direction, clicked face, and click position within the block.
  - So stairs, observers, pistons, dispensers/droppers, hoppers, repeaters (delay), comparators (mode), rails, chests (single vs double), door hinges, logs (axis), crafter orientation and banners/signs (rotation) can come out wrong unless the player manually looks in the right direction.
  - Forcing V2 or V3 there produces ghost blocks, because the server rejects the out-of-range hit vector.
  This follows from the code and the 1.18.2 check described above.
- For a Fabric 26.3 technical server, Servux is the only maintained way to get full-orientation Easy Place. Carpet alone does not provide `accurateBlockPlacement`: that rule lives in Carpet Extra/QuickCarpet per the tooltip, and Carpet Extra has no 26.3 build. If a future Carpet Extra 26.3 is installed alongside Servux, Servux's mixin is designed to override it (priority comment), and the client's Auto mode would pick V3 anyway because Servux detection is checked first.
- Servux's default `permission_level_easy_place` = 0 means all players can use V3 out of the box. Admins wanting to restrict it can raise the level or use permission nodes.

### Gaps
- The exact date and author of the first V3 implementation (Litematica side, likely masa pre-2024; Servux side, likely sakura-ryoko in 2024 after Servux 0.2.0 on 2024-06-13) could not be confirmed. GitHub commit-history API calls were rate-limited and the Servux 0.3.x Modrinth version pages now 404.
- The Servux `MixinServerGamePacketListenerImpl_easyPlace.java` source was not read line by line. That it bypasses the 1.18.2 hit-vector check server-side is inferred from the file name and the Litematica counterpart.
- The allowed values of Leaves' `alternative-block-placement` (e.g. CARPET / LITEMATICA / MASA_V3?) and whether Leaves' Servux emulation triggers Litematica's `hasServuxServer()` detection (and thus Auto=V3) were not confirmed for Leaves 26.3.
- Whether `EntityDataManager.hasServuxServer()` requires the client's `entityDataSync` to be enabled was not checked (relevant to whether Auto picks V3 with default client configs).

---

## 2. Other server-dependent Litematica features (saving NBT, verifier, material list, paste, sharing)

### Takeaway
Saving schematics with real block-entity and entity NBT in multiplayer needs **Servux `entity_data`** plus the client toggle `entityDataSync` (default **false**), or the op-only vanilla NBT-query fallback `entityDataSyncBackup`. Fast, NBT-complete server-side pasting needs **Servux `litematic_data`** with creative mode. Without Servux, paste uses `/setblock`/`/fill`/`/summon` commands that require op (level 2), and container NBT is not restored reliably. Schematic sharing between players is the separate **Syncmatica** mod, which must be on both server and client.

### Cited Findings
**Entity data sync (saving NBT, info overlay)**
- `entityDataSync` (ConfigBooleanHotkeyed, default false): "Use the Entity Data Sync protocol from Servux to obtain Entity Data from the server". — [Configs.java L91](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/config/Configs.java); [en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)
- `entityDataSyncBackup` (default false): "Use the Vanilla NBT Query method when Servux is not available. This method requires Operator Privileges." — same sources
- `entityDataSyncCacheTimeout` (default 2.75 s, range 1-100): "consider a higher value if your litematics fail to save with all of the NBT data." — same sources
- Litematica 0.19.54 (2024-12-22): "Make it so that the entityDataSyncBackup mode is capable of saving Litematics with Server-side NBT data, similar to how Servux functions." Litematica 0.20.4 (2025-03-02): "convert it into a Boolean Hotkey, & make the config disabled by default". — [Modrinth Litematica versions API](https://api.modrinth.com/v2/project/litematica/version)
- The Block Info Overlay and `renderInfoOverlay` tooltips say: "NOTE: This feature requires 'entityDataSync' to be enabled via Servux on servers." — [en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)
- Servux `entity_data` provider settings:
  - `permission_level` default 0.
  - `nbt_query_override` plus `nbt_query_permission_level` (default 2) overrides vanilla's op-2 NBT-query permission.
  - `nbt_allow_player_inventory` and `nbt_allow_player_ender_items`, each with a permission level defaulting to 2.
  — [EntitiesDataProvider.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/dataproviders/EntitiesDataProvider.java); [Servux en_us.json](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/resources/assets/servux/lang/en_us.json)

**Paste in multiplayer**
- Without Servux, command-based paste uses:
  - `commandLimitPerTick` and `commandTaskInterval` to set the rate.
  - `commandNameSetblock`, `commandNameClone` and `commandNameSummon` for command names.
  - `commandDisableFeedback`, which toggles the sendCommandFeedback gamerule.
  - `pasteUseFillCommand`.
  - `commandUseWorldEdit`, which uses //pos1 //pos2 //set and is about 3x slower; "the paste replace behavior option WILL NOT WORK" with it.
  — [en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)
- `pasteNbtRestoreBehavior` options are "Place & Data Modify", "Place & Clone" and "Teleport & Place". The tooltip says teleport doesn't work. For Place & Data Modify "you will probably need to lower the pasteCommandLimit to 1 per tick", and it is recommended only for important blocks such as inventories. — same source
- `pasteUsingServux` (default **true**): "Use Servux to paste a schematic directly to the server. This method is much faster than the traditional command-based method, and it supports restoring Entity NBT Data. NOTE: This feature requires 'entityDataSync' to be enabled via Servux on servers." — same source; [Configs.java L119](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/config/Configs.java)
- Servux `litematic_data` settings:
  - `permission_level`, `permission_level_paste` and `permission_level_tasks` (all default 0).
  - `fix_chest_mirror`, `fix_rail_rotations` and `fix_stairs_mirror`.
  - `deduplicate_schematic_entities`, `paste_always_use_persistent` and `player_task_feedback`.
  — [LitematicsDataProvider.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/dataproviders/LitematicsDataProvider.java); [Servux en_us.json](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/resources/assets/servux/lang/en_us.json)
- Servux 0.9.7 (2026-08-29): "add: task permission nodes and 'permission_level_tasks' config; also check that they are in Creative Mode." Litematica 0.26.13 (2026-08-20) added "Data Tag Compression packets ... greatly improve's Servux Pasting upload speed; and transition to the Servux Task Scheduler for Servux Paste", plus "Task Fill / Delete to Servux". — [Servux versions API](https://api.modrinth.com/v2/project/servux/version); [Litematica versions API](https://api.modrinth.com/v2/project/litematica/version)
- Guide (2026-10-31): Servux "still requires creative mode for pastes, fills and deletes". To restrict to ops, set both `litematic_data` paste and task levels to 2 via `servux set`, then `servux save`; `servux set` requires level 4. Without Servux, `/setblock` and `/fill` need permission level 2. On Paper, Paper's `packet-limiter` can kick during a paste. — [space-node.net](https://space-node.net/blog/litematica-multiplayer-server-syncmatica-servux-2026)
- Fallen-Breath's litematica-server-paster v1.3.14-mc26.3 (2026-09-26) exists for 26.3. It requires Litematica, and the guide calls it a Fabric mod that restores container NBT for command paste. — [Modrinth API](https://api.modrinth.com/v2/project/litematica-server-paster/version?game_versions=%5B%2226.3%22%5D); [space-node.net](https://space-node.net/blog/litematica-multiplayer-server-syncmatica-servux-2026)
- For Paper/Folia, LitematicaFolia "speaks enough of the Servux wire protocol that a vanilla Litematica client can paste directly to the server". Its newest builds are 0.8.0+26.2 and 0.4.3+26.1.2 (2026-08-29), with **no 26.3** yet. — [Modrinth litematicafolia API](https://api.modrinth.com/v2/project/litematicafolia/version)

**Material list and verifier**
- `materialListContainerScan`: "Scan your last opened containers to resort your active Material List. Added from Stormatica by CubicMetre". There are sub-options for shulkers and bundles, and `materialListCountEnderCache` (requires MaLiLib `enableChestDataTracker`). — [en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)
- Litematica 0.29.1 added "Pick Stackable entities to Material List" and an "Item Frame override for Entities in Material List". — [Modrinth Litematica 26.3 API](https://api.modrinth.com/v2/project/litematica/version?game_versions=%5B%2226.3%22%5D)
- Verifier option `enableDifferentBlocks` shows a "Different Blocks" status (for example white glass vs glass) when only the block type differs within a tag group. — [en_us.json](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/resources/assets/litematica/lang/en_us.json)

**Schematic sharing (Syncmatica)**
- Syncmatica 0.3.20 for 26.3 (2026-09-22). On Modrinth it is `client_side: required, server_side: required`, and the source is sakura-ryoko/syncmatica, a fork of End-Tech/syncmatica. — [Modrinth Syncmatica 26.3 API](https://api.modrinth.com/v2/project/syncmatica/version?game_versions=%5B%2226.3%22%5D); [project API](https://api.modrinth.com/v2/project/syncmatica); [GitHub API](https://api.github.com/repos/sakura-ryoko/syncmatica)
- Syncmatica changelogs:
  - 0.3.14: `/syncmatica load` command and `DISPLAY_NAME` feature.
  - 0.3.16: "fix: fabric-permissions-api (for luck perms)".
  - 0.3.19: "Sanitize the communicated file name to be saved under the placements.json".
  — [Modrinth Syncmatica versions API](https://api.modrinth.com/v2/project/syncmatica/version)
- Guide: the server stores shared files in a `syncmatics` folder and placements in `world/syncmatica/placements.json`. The upload quota is off by default (40 MB when enabled). Only `.litematic` files can be shared. The guide warns the 26.3 code lets anyone remove a shared placement for everyone. — [space-node.net](https://space-node.net/blog/litematica-multiplayer-server-syncmatica-servux-2026)
- Leaves has built-in Syncmatica support (`settings.protocol.syncmatica.enable`, quota, `quota-limit: 40000000`). — [Leaves docs](https://docs.leavesmc.org/leaves/reference/configuration)

### Inferences
- Recommended server-side set for a Fabric 26.3 technical-survival server running Litematica: Servux 0.12.2, Syncmatica 0.3.20 (server copy), and optionally litematica-server-paster. Players must turn on `entityDataSync` client-side for NBT-complete saves and for Servux paste.
- On survival servers, Servux paste and fill tasks require creative mode, so paste is a creative or staff tool. Easy Place is the survival feature.

### Gaps
- The verifier's accuracy for block-entity contents (does it compare inventories/NBT, or only block states?) was not confirmed from source. The verifier compares against the client world, so states should be accurate in loaded chunks, but NBT comparison is unverified.
- Litematica's built-in "Schematic Placement sharing" (a share-link/placement export feature in newer builds) was not located in the 26.3 lang file under that name. I found no reliable source that it exists as a server feature.

---

## 3. Tweakeroo placement features and server support / anti-cheat

### Takeaway
Tweakeroo's `tweakFlexibleBlockPlacement` and `tweakAccurateBlockPlacement` rotate blocks using the same Carpet/V3 protocol as Litematica's `accuratePlacementProtocol` / `accuratePlacementProtocolMode`. So they need **Servux (V3)** or Carpet Extra (V2, not available for 26.3) on the server for anything beyond clicked-face-only blocks. Fast placement, fast right click and hand restock are pure client input automation and need no server support, but their packet rate is what anti-cheat and Paper's packet limiter react to.

### Cited Findings
- `accuratePlacementProtocol`: "If enabled, then the Flexible Block Placement and the Accurate Block Placement use the protocol implemented in Carpet mod. Note: This is required for any block rotations to work, other than blocks that only care about the block side you click on (Hoppers, Logs etc.)" — [Tweakeroo 26.3 en_us.json](https://raw.githubusercontent.com/sakura-ryoko/tweakeroo/26.3/src/main/resources/assets/tweakeroo/lang/en_us.json)
- `accuratePlacementProtocolMode` uses the same Auto/V3/V2/Slabs-only text as Litematica: "Version 3: Supported by Tweakeroo itself (in single player) or with Servux." — same source
- `tweakAccurateBlockPlacement`: "a simpler version of Flexible placement, similar to the Carpet mod, so basically either facing into or out from the block face clicked on". `tweakFlexibleBlockPlacement`: "placing blocks in different orientations or with an offset". — same source
- Other building tweaks:
  - `tweakHandRestock` (with `handRestockPre`).
  - `tweakFastRightClick` (`fastRightClickCount` per tick).
  - Fast Block Placement (`fastPlacementRememberOrientation`).
  - `tweakPlacementRestriction` (Plane/Layer/Face/Column/Line/Diagonal).
  - `tweakAfterClicker` (auto-click to set repeater delay).
  - `tweakBlockReachOverride`: "Do not attempt to use this at a value beyond [0.5 - 1.0] higher than the Rules defined on a server."
  — same source
- Tweakeroo label: "Note: This feature works either at all or at least fully only in single player; or while connected to Servux with 'entityDataSync' enabled". Tweakeroo 0.21.51 added "Support for Servux for inventoryPreview using the Tweaks Data Provider". — same source; [Modrinth Tweakeroo versions API](https://api.modrinth.com/v2/project/tweakeroo/version)
- Tweakeroo 0.30.1 (2026-09-27, 26.3): "fix / check placement tweaks"; "Fix the slimeBlockSlowdown causing non-vanilla behaviour on integrated servers". 0.30.0 is dated 2026-09-21. — [Modrinth Tweakeroo 26.3 API](https://api.modrinth.com/v2/project/tweakeroo/version?game_versions=%5B%2226.3%22%5D)
- An anti-cheat example: a player was "kicked for placing blocks too quickly with litematica". — [EcoCityCraft forum](https://ecocitycraft.com/threads/anti-cheat-report-kicked-for-placing-blocks-too-quickly-with-litematica-while-in-my-town.224946/)
- The Paper plugin AntiLitematica "detects and prevents the use of Litematica, Schematica, and their Printer features". — [Hangar AntiLitematica](https://hangar.papermc.io/LinQingDev_/AntiLitematica)

### Inferences
- For a Fabric server with Servux and no anti-cheat, all Tweakeroo placement tweaks work fully. On Paper, rotation tweaks degrade (ghost blocks if the protocol is forced, wrong facing otherwise) unless a Paper accurate-placement plugin is present, and none has a 26.3 build yet. High fastRightClick/fastPlacement rates risk anti-cheat kicks.

### Gaps
- No primary source tests Tweakeroo against specific Paper anti-cheats (Grim, Vulcan and similar) on 26.3. I found no reliable data.

---

## 4. MiniHUD features needing server data (structures, spawn chunks, seed, slime chunks) and 26.x changes

### Takeaway
On a server, MiniHUD gets structure bounding boxes from **Servux `structure_bounding_boxes`** (default level 0). The world seed for the slime-chunk overlay, spawn point, weather, TPS and mob caps come from **Servux `hud_data`**. Servux shares the seed by default only with permission level ≥ 2, so non-op players need `seed_permission_level` lowered or must enter the seed manually.

### Cited Findings
- `hudDataSync`: "Use the HUD Data Sync protocol from Servux to obtain various Info Line Data from the server. This is used by settings such as 'infoWeather', 'infoFurnaceXP', and can get the World Seed and Spawn Chunk information". — [MiniHUD 26.3 en_us.json](https://raw.githubusercontent.com/sakura-ryoko/minihud/26.3/src/main/resources/assets/minihud/lang/en_us.json)
- `infoSlimeChunk`: "NOTE: This only works in single player without any user intervention! On a server the player needs to either: 1) be admin/OP and run the /seed command manually EVERY TIME they join or change dimensions, or 2) input the seed via chat, by sending a 'command' like: minihud-seed 12345". — same source
- `debugStructuresEnabled`: "Toggles the vanilla Structures debug renderer. NOTE: This option requires OP Privileges on a server." — same source
- Servux `hud_data` settings: `permission_level` 0, `share_seed`, `seed_permission_level` **2**, `share_weather_status`, `weather_permission_level` 0, `loggers_enabled`/`loggers_enable_list` (TPS, mob caps), `logger_permission_level` 0, `update_interval`. — [HudDataProvider.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/dataproviders/HudDataProvider.java); [Servux en_us.json](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/resources/assets/servux/lang/en_us.json)
- Servux `structure_bounding_boxes` settings: `permission_level` 0, `structures_blacklist(_enabled)`, `structures_whitelist(_enabled)`, `update_interval`, `timeout`. — [StructureDataProvider.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/dataproviders/StructureDataProvider.java); [Servux en_us.json](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/resources/assets/servux/lang/en_us.json)
- MiniHUD history:
  - 0.32.51 added "Servux support for sending the World Seed, and Weather information (REQUIRES Servux 0.3.8)".
  - 0.36.1 (2025-06-30) added receiving `infoServerTPS`/`infoMobCaps` from Servux's Data Logger.
  - 0.37.2 (2025-10-20, 1.21.9): "Re-Enable spawn chunks walls; but only if you use the `#minihud-spawnchunkradius` pseudo command to set the radius."
  - 0.37.4 (2025-11-28): "due to Vanilla changes; some debug renderers are being added/removed/changed -- this also means that the Servux `debug_data` protocol is obsolete since all you need now is OP privileges on any server to use these features."
  - 0.38.0 (1.21.11): `ExpandBox` tag from Servux structure data.
  — [Modrinth MiniHUD versions API](https://api.modrinth.com/v2/project/minihud/version)
- MiniHUD 26.x releases: 0.39.0 (2026-03-25, 26.1, "Villager Info Overlay not rendering due to 26.1 rendering changes"), 0.40.0 (2026-06-17, 26.2), 0.41.0 (2026-09-21), 0.41.1 (2026-09-22) and 0.41.2 (2026-09-27, 26.3, "add: infoLineSneaking"). — same source; [MiniHUD 26.3 API](https://api.modrinth.com/v2/project/minihud/version?game_versions=%5B%2226.3%22%5D)
- MiniHUD has its own `entityDataSync` / `entityDataSyncBackup` (backup requires op). — [MiniHUD en_us.json](https://raw.githubusercontent.com/sakura-ryoko/minihud/26.3/src/main/resources/assets/minihud/lang/en_us.json)
- Leaves equivalents: `hud-metadata-protocol` (+ `-share-seed: true`) and `structure-protocol`. — [Leaves docs](https://docs.leavesmc.org/leaves/reference/configuration)

### Inferences
- Since vanilla 1.21.9 replaced fixed spawn chunks with a configurable radius, MiniHUD's "real" spawn-chunk overlay on 26.x depends on the player entering the radius via `#minihud-spawnchunkradius`, or on Servux spawn metadata (`refreshSpawnMetadata` in HudDataProvider). It is not automatic from the old fixed 11/12-chunk logic.
- Admins who want everyone to see slime chunks should set Servux `hud_data.seed_permission_level` (and `structure_bounding_boxes.seed_permission_level`) to 0.

### Gaps
- Exactly what the 26.3 Servux spawn metadata contains (spawn position plus radius?) was not read in full.

---

## 5. Litematica printer forks: 26.3 status and server and anti-cheat interaction

### Takeaway
The Modrinth project "litematica-printer" is now maintained by sakura-ryoko, as a fork of aleksilassila's original, which was last pushed 2024-11-24. Version 3.2.3 for 26.3 was released 2026-09-27. It is client-only, has no "legit mode" for anticheats, and is a common target of anti-Litematica plugins. It needs no server mod, but it benefits from the same Servux V3 support for correct orientations.

### Cited Findings
- Modrinth `litematica-printer` (id 3llatzyE) has source_url https://github.com/sakura-ryoko/litematica-printer and is described as "This fork adds the missing printing functionality for Litematica". It is `client_side: required, server_side: unsupported`. — [Modrinth project API](https://api.modrinth.com/v2/project/litematica-printer)
- Version 3.2.3 (2026-09-27, 26.3): "Fix disconnect when moving while printing (#42)". 3.2.2 for 26.3 is dated 2026-09-22. It requires Litematica and MaLiLib. — [Modrinth 26.3 API](https://api.modrinth.com/v2/project/litematica-printer/version?game_versions=%5B%2226.3%22%5D)
- 3.2.1+1.21.10 (2025-12-16) added "`printInAir` feature to allow placing blocks without support (#29)". — [Modrinth versions API](https://api.modrinth.com/v2/project/litematica-printer/version)
- sakura-ryoko/litematica-printer is a fork of aleksilassila/litematica-printer, default branch `26.3`, pushed 2026-10-01. The original was last pushed 2024-11-24. — [GitHub API fork](https://api.github.com/repos/sakura-ryoko/litematica-printer); [GitHub API original](https://api.github.com/repos/aleksilassila/litematica-printer)
- The README covers a CAPS_LOCK toggle and speed/range in the Litematica Generic tab. Its known issues include a missing "legit mode" for anticheats, liquids not placeable, and an imperfect rail algorithm. — [GitHub README](https://github.com/sakura-ryoko/litematica-printer)
- The Paper plugin AntiLitematica targets "Litematica, Schematica, and their Printer features". — [Hangar](https://hangar.papermc.io/LinQingDev_/AntiLitematica)

### Inferences
- On the planned server (presumably Fabric plus Servux), the printer will work with full orientations through Servux's V3 handling. Whether to allow it is a server-rules decision, since no server mod can see it beyond packet patterns.

### Gaps
- No source describes the 26.3 printer's exact packet behaviour (rotation packets, per-tick rate). AntiLitematica's 26.3 compatibility was not verified.

---

## 6. Recommended client mod list for 26.3 technical survival (versions and dates)

### Takeaway
Everything core exists for 26.3 as of 2026-11-17. The gaps are **Carpet Extra** (no 26.3), **Sodium** (26.3 builds are still beta: mc26.3-0.9.3-beta.5), and **Litemoretica**, LitematicaFolia and the Paper accurate-placement plugin (no 26.3 builds). Minecraft 26.3 requires Java 25.

### Cited Findings
All versions below come from the Modrinth API filtered to game version 26.3 (`https://api.modrinth.com/v2/project/<slug>/version?game_versions=["26.3"]`), queried 2026-11-17.

| Mod | Side | Latest 26.3 version | Date | Notes / source |
|---|---|---|---|---|
| Fabric Loader | both | 0.20.1 (stable) | n/a | [Fabric meta](https://meta.fabricmc.net/v2/versions/loader/26.3); 26.4 snapshots exist (26.4-snapshot-8) — [meta game](https://meta.fabricmc.net/v2/versions/game) |
| Fabric API | both | 0.166.2+26.3 | 2026-11-11 | [API](https://api.modrinth.com/v2/project/fabric-api/version?game_versions=%5B%2226.3%22%5D) |
| MaLiLib | client | 0.30.2 | 2026-09-27 | 0.30.1 "Remove expimental Sodium mixin"; 0.30.2 "experimental: SDL Gamepad handling for Keybinds" — [API](https://api.modrinth.com/v2/project/malilib/version?game_versions=%5B%2226.3%22%5D) |
| Litematica | client | 0.29.1 | 2026-09-27 | 0.29.0 (2026-09-22) "fix sodium compat … 26.3 'works' with shaders more or less; minus the texture problem" — [API](https://api.modrinth.com/v2/project/litematica/version?game_versions=%5B%2226.3%22%5D) |
| MiniHUD | client | 0.41.2 | 2026-09-27 | [API](https://api.modrinth.com/v2/project/minihud/version?game_versions=%5B%2226.3%22%5D) |
| Tweakeroo | client | 0.30.1 | 2026-09-27 | [API](https://api.modrinth.com/v2/project/tweakeroo/version?game_versions=%5B%2226.3%22%5D) |
| Item Scroller | client | 0.33.1 | 2026-09-27 | slug `item-scroller`; 0.33.0 on 2026-09-21 — [API](https://api.modrinth.com/v2/project/item-scroller/version) |
| Syncmatica | **both** | 0.3.20 | 2026-09-22 | [API](https://api.modrinth.com/v2/project/syncmatica/version?game_versions=%5B%2226.3%22%5D) |
| Servux | **server only** | 0.12.2 | 2026-09-27 | README: "Servux itself is never needed on the clients or in single player" — [README](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/README.md); [API](https://api.modrinth.com/v2/project/servux/version?game_versions=%5B%2226.3%22%5D) |
| Carpet | server (client optional) | 26.3 | 2026-09-18 | [API](https://api.modrinth.com/v2/project/carpet/version?game_versions=%5B%2226.3%22%5D) |
| Carpet Extra | server | **none for 26.3** (latest 26.2, 2026-06-21) | n/a | [API](https://api.modrinth.com/v2/project/carpet-extra/version) |
| litematica-server-paster | both (Fabric) | v1.3.14-mc26.3 | 2026-09-26 | [API](https://api.modrinth.com/v2/project/litematica-server-paster/version?game_versions=%5B%2226.3%22%5D) |
| TweakerMore | client | v3.33.3-beta.1-mc26.3 (beta) | 2026-09-26 | [API](https://api.modrinth.com/v2/project/tweakermore/version?game_versions=%5B%2226.3%22%5D) |
| Litematica Printer | client | 3.2.3 | 2026-09-27 | [API](https://api.modrinth.com/v2/project/litematica-printer/version?game_versions=%5B%2226.3%22%5D) |
| Jade | client (+server optional) | 26.3.5+fabric | 2026-10-02 | [API](https://api.modrinth.com/v2/project/jade/version?game_versions=%5B%2226.3%22%5D) |
| WTHIT | client | fabric-21.0.0 | 2026-11-08 | [API](https://api.modrinth.com/v2/project/wthit/version?game_versions=%5B%2226.3%22%5D) |
| AppleSkin | client | 3.0.10+mc26.3 | 2026-09-17 | [API](https://api.modrinth.com/v2/project/appleskin/version?game_versions=%5B%2226.3%22%5D) |
| Xaero's Minimap | client | fabric-26.3-26.6.2 | 2026-10-25 | [API](https://api.modrinth.com/v2/project/xaeros-minimap/version?game_versions=%5B%2226.3%22%5D) |
| Xaero's World Map | client | fabric-26.3-1.47.2 | 2026-10-25 | [API](https://api.modrinth.com/v2/project/xaeros-world-map/version?game_versions=%5B%2226.3%22%5D) |
| JourneyMap | client | 26.3-6.0.10 (+paper/neoforge/forge builds listed) | 2026-10-03 | [API](https://api.modrinth.com/v2/project/journeymap/version?game_versions=%5B%2226.3%22%5D) |
| Sodium | client | mc26.3-0.9.3-beta.5-fabric (**beta**) | 2026-11-12 | [API](https://api.modrinth.com/v2/project/sodium/version?game_versions=%5B%2226.3%22%5D) |
| Iris | client | 1.11.7+26.3-fabric | 2026-09-30 | [API](https://api.modrinth.com/v2/project/iris/version?game_versions=%5B%2226.3%22%5D) |
| Axiom (alt. building tool) | both | 6.1.5 | 2026-10-28 | [API](https://api.modrinth.com/v2/project/axiom/version?game_versions=%5B%2226.3%22%5D) |

- Modrinth side metadata:
  - Litematica: client required, server unsupported.
  - Item Scroller: client required, server unsupported.
  - Servux: client unsupported, server required.
  - Syncmatica: required on both.
  — [Litematica](https://api.modrinth.com/v2/project/litematica), [Item Scroller](https://api.modrinth.com/v2/project/item-scroller), [Servux](https://api.modrinth.com/v2/project/servux), [Syncmatica](https://api.modrinth.com/v2/project/syncmatica)
- Guide (2026-10-31): "26.3 runs on Java 25". Its version table for 26.3 is Litematica 0.29.1 + MaLiLib 0.30.2, Servux 0.12.2, Syncmatica 0.3.20, Server Paster 1.3.14, which matches the API. — [space-node.net](https://space-node.net/blog/litematica-multiplayer-server-syncmatica-servux-2026)
- Item Scroller's mass crafting has a Servux side: `scroller_data.mass_craft_permission_level`. — [Servux en_us.json](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/resources/assets/servux/lang/en_us.json)

### Inferences
- Minimal client pack: Fabric Loader 0.20.1, Fabric API 0.166.2+26.3, MaLiLib 0.30.2, Litematica 0.29.1, MiniHUD 0.41.2, Tweakeroo 0.30.1, Item Scroller 0.33.1, and Syncmatica 0.3.20 if the server runs it.
- Optional QoL: Jade 26.3.5 or WTHIT 21.0.0, AppleSkin 3.0.10, Xaero's Minimap/World Map, Sodium 0.9.3-beta.5 (beta), Iris 1.11.7, TweakerMore (beta).
- Carpet on the client is optional. It is only needed for client-side Carpet features or scarpet, not for Litematica.
- Server pack (Fabric): Fabric API, Servux 0.12.2, Carpet 26.3, Syncmatica 0.3.20, and optionally litematica-server-paster and Jade's server-side addon.

### Gaps
- The Fabric Loader 0.20.1 release date was not retrieved.
- Jade/WTHIT server-side data plugins for 26.3 were not checked.

---

## 7. Known issues: Litematica + Sodium/Iris rendering, the sakura-ryoko maintenance model, 26.x breaking changes

### Takeaway
The 26.3 masa mods are maintained by sakura-ryoko, and masa stopped updating the modern Fabric line after 1.20.4. Litematica fixed Sodium compatibility in 0.29.0. MaLiLib removed its experimental Sodium mixin in 0.30.1. Shaders mostly work, with a texture problem noted, and Sodium for 26.3 is still beta. A notable 26.x platform change is the vanilla permission API (`Entity.checkPermission(Identifier, PermissionLevel)`), which Servux now uses for permission nodes.

### Cited Findings
- Litematica 0.29.0 (2026-09-22): "fix sodium compat. NOTE: It seems that 26.3 'works' with shaders more or less; minus the texture problem." — [Modrinth Litematica 26.3 API](https://api.modrinth.com/v2/project/litematica/version?game_versions=%5B%2226.3%22%5D)
- MaLiLib 0.30.1 (2026-09-22): "Remove expimental Sodium mixin". — [Modrinth MaLiLib 26.3 API](https://api.modrinth.com/v2/project/malilib/version?game_versions=%5B%2226.3%22%5D)
- Earlier history: Litematica 0.20.4 (2025-03-02) "fix Sodium / Shaders compat". — [Modrinth Litematica versions API](https://api.modrinth.com/v2/project/litematica/version)
- Sodium 0.9.3-beta.5 (2026-11-12) "Added compatibility metadata for Fabric and NeoForge builds to prevent usage in broken configurations". 26.3 Sodium builds are all `beta`. — [Modrinth Sodium 26.3 API](https://api.modrinth.com/v2/project/sodium/version?game_versions=%5B%2226.3%22%5D)
- Servux 0.2.0 note by masa: no plans to update the pre-rewrite code after 1.20.4. — [Modrinth Servux versions API](https://api.modrinth.com/v2/project/servux/version)
- The forks of maruohon's litematica, servux, minihud and tweakeroo all have default branch `26.3`, last pushed 2026-11-11 (Litematica), 2026-10-01 (Servux), 2026-11-15 (MiniHUD) and 2026-11-09 (Tweakeroo), so work continues after the 0.29.1/0.41.2/0.30.1 Modrinth releases. — [GitHub API litematica](https://api.github.com/repos/sakura-ryoko/litematica), [servux](https://api.github.com/repos/sakura-ryoko/servux), [minihud](https://api.github.com/repos/sakura-ryoko/minihud), [tweakeroo](https://api.github.com/repos/sakura-ryoko/tweakeroo)
- Servux PermissionsUtil uses `PermissionLevel.byId`, `entity.checkPermission(Identifier, PermissionLevel)` and `Permission.HasCommandLevel`, which are 26.x vanilla permission types. — [PermissionsUtil.java](https://raw.githubusercontent.com/sakura-ryoko/servux/26.3/src/main/java/fi/dy/masa/servux/util/PermissionsUtil.java)
- Litematica 26.3 code uses Mojang official mappings (e.g. `ServerGamePacketListenerImpl`, `BlockStateProperties`, `Identifier`). — [PlacementHandler.java](https://raw.githubusercontent.com/sakura-ryoko/litematica/26.3/src/main/java/fi/dy/masa/litematica/util/PlacementHandler.java)
- MiniHUD 0.39.0 (26.1): "Villager Info Overlay not rendering due to 26.1 rendering changes". — [Modrinth MiniHUD versions API](https://api.modrinth.com/v2/project/minihud/version)

### Inferences
- New commits since the last Modrinth releases (late September) suggest further 26.3 point releases (e.g. Litematica 0.29.2) may follow. The server plan should pin versions and re-check Modrinth before launch.
- Pair Litematica 0.29.x with the newest Sodium beta. If schematic rendering glitches appear, test without Iris shaders first, given the noted "texture problem".

### Gaps
- No specific open GitHub issues for Litematica + Sodium 0.9.3-beta on 26.3 were retrieved (GitHub API rate limit). Reddit/Bilibili/MCMod reports for 26.3 were not found.
