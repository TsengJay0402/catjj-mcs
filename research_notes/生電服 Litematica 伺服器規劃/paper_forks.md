# Paper-family server software for a Minecraft Java 26.3 technical-survival (生電) server with Litematica Easy Place V3

Research date: 2026-11-17. All availability data was pulled live from project APIs and GitHub on this date unless noted. Version tags: **[26.3]** = confirmed for 26.3; **[1.21.11]** = confirmed only for 1.21.11 or older; **[docs, version unknown]** = from a docs page that doesn't state its version.

## Q1. Leaves (LeavesMC): 26.3 availability, protocols, restored vanilla behaviour

### Takeaway
**There is no Leaves build for any 26.x version (26.1/26.2/26.3) as of 2026-11-17.** The newest official build is `1.21.11-157` (2026-08-13), and GitHub marks every Leaves release as a prerelease. A community PR that ports Leaves to 26.1.2 is still open and unmerged. On paper, Leaves has the most complete server-side protocol set of any Paper fork: Easy Place V3 (`alternative-block-placement: LITEMATICA`), Servux, Syncmatica, PCA, BBOR, Jade, AppleSkin, Xaero, Carpet fake players, and more. It also has a one-switch "technical survival mode" that turns off Paper's anti-exploit fixes. **But you can't run it on 26.3 today.** Its code lives on in Lophine, a Folia-based fork that does have 26.3 builds (see Q3).

### Cited Findings
**Availability and status**
- Latest Leaves GitHub releases: `1.21.11-157-a8bb272` (2026-08-13), `1.21.11-156` (2026-07-20), `1.21.11-155` (2026-07-20), `1.21.11-154` (2026-05-03). All are flagged prerelease. — [GitHub API releases](https://api.github.com/repos/LeavesMC/Leaves/releases) / [Releases page](https://github.com/LeavesMC/Leaves/releases)
- Leaves download API version list ends at `1.21.11`. There is no 26.x entry. — [api.leavesmc.org/v2/projects/leaves](https://api.leavesmc.org/v2/projects/leaves)
- The mcjars.app index also has no Leaves 26.3 build. — [mcjars API](https://mcjars.app/api/v2/builds/LEAVES)
- The `master` branch `gradle.properties` still reads `mcVersion=1.21.11`, `preVersion=true`. The last master commit is 2026-08-13 ("fix: correct region-unload-idle-ms unit handling (#878)"). Branches include `dev/1.21.11` but no 26.x branch. — [gradle.properties](https://raw.githubusercontent.com/LeavesMC/Leaves/master/gradle.properties); [branches](https://github.com/LeavesMC/Leaves/branches)
- PR #846 "升级到 26.1（测试）" (upgrade to 26.1, test) was opened 2026-04-21 and **closed without merge** on 2026-06-03. It carried a warning: "目前仍为 26.1 测试版本…谨慎在生产环境中使用" (still a 26.1 test build; use in production with caution). It covered the jump 1.21.10 → 1.21.11 → 26.1 → 26.1.2 and dropped patches that upstream had absorbed (vanilla fluid pushing, climb-check cache, spooky-season check). The old config keys stay behind as `@Deprecated(forRemoval = true, since = "26.1.2")`. — [PR #846](https://github.com/LeavesMC/Leaves/pull/846)
- PR #863 "更新 26.1.2" (update to 26.1.2, built against Paper stable) is **still open**. The last activity, 2026-09-10, is a user comment "期待大佬们的 PR" ("looking forward to the experts' PR"). — [PR #863](https://github.com/LeavesMC/Leaves/pull/863)
- Issue #871 "我们需要26.1和26.2" ("we need 26.1 and 26.2"), 2026-07-17, was closed as a duplicate pointing to #863. No release timeline was given. — [Issue #871](https://github.com/LeavesMC/Leaves/issues/871)
- Recent Leaves issues (Aug–Oct 2026) are all against 1.21.11. Examples: #884 hopper-minecart comparator update differs from vanilla (open); #880 PR "fix several update-suppression crashes" (open); #886 "Leaves 1.21.11 incompatible with Geyser". — [Leaves issues](https://github.com/LeavesMC/Leaves/issues)
- Official docs: https://docs.leavesmc.org redirects to `/en/leaves/reference/configuration`. The source is the LeavesMC/Documentation repo, whose config spec still contains notes such as "As of this document update (1.21.4-34)". — [docs redirect](https://docs.leavesmc.org/en/leaves/reference/configuration); [config spec en.yml](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/config-spec/leaves/en.yml)
- The LeavesMC org also runs **Lumina**, described as "A new generation of multi-threaded servers designed for large technical servers". Its last push was 2025-08-04, on branch `dev/1.21.6`, so it's effectively dormant. — [LeavesMC org repos](https://github.com/orgs/LeavesMC/repositories)

**Protocol support (leaves.yml, `settings.protocol.*`). Source code is the 1.21.11 master, so it is [1.21.11] only.**
- `alternative-block-placement`: `NONE | CARPET` (accurate placement protocol v2) `| CARPET_FIX` (needs MasaGadget on the client) `| LITEMATICA` (accurate placement protocol **v3**, i.e. Litematica Easy Place V3). The default is `NONE`. — [config spec](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/config-spec/leaves/en.yml); [LeavesConfig.java](https://raw.githubusercontent.com/LeavesMC/Leaves/master/leaves-server/src/main/java/org/leavesmc/leaves/LeavesConfig.java)
- Any value other than `NONE` automatically sets `modify.disableDistanceCheckForUseItem = true`, which removes the use-item hit-distance check. — [LeavesConfig.java](https://raw.githubusercontent.com/LeavesMC/Leaves/master/leaves-server/src/main/java/org/leavesmc/leaves/LeavesConfig.java)
- `servux.structure-protocol`, `servux.entity-protocol`, `servux.hud-metadata-protocol` (with `hud-metadata-protocol-share-seed`, default true), `servux.hud-logger-protocol`, and `hud-enabled-loggers` (default TPS, MOB_CAPS). All default to false. — [LeavesConfig.java](https://raw.githubusercontent.com/LeavesMC/Leaves/master/leaves-server/src/main/java/org/leavesmc/leaves/LeavesConfig.java)
- `servux.litematics.enable` (default false) plus `servux.litematics.max-nbt-size` (default 2097152). Enabling it registers the permission `leaves.protocol.litematics`, default OP. This is Servux's Litematica server-paste channel. The docs spec still lists the older key `servux.litematics-protocol`, which the code migrates via `@TransferConfig`. — [LeavesConfig.java](https://raw.githubusercontent.com/LeavesMC/Leaves/master/leaves-server/src/main/java/org/leavesmc/leaves/LeavesConfig.java)
- `syncmatica.enable`, with `quota` / `quota-limit` (default 40000000 bytes). — [config spec](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/config-spec/leaves/en.yml)
- `pca.pca-sync-protocol` (Plusls Carpet Addition container/entity sync), with `pca-sync-player-entity` = `NOBODY | BOT | OPS` (default) `| OPS_AND_SELF | EVERYONE`. — [config spec](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/config-spec/leaves/en.yml)
- Also in the config: `bbor-protocol`, `jade-protocol`, `appleskin.protocol` (+ `sync-tick-interval`), `xaero-map-protocol` (+ `xaero-map-server-id`), `leaves-carpet-support` (only *advertises* Carpet to clients, "does NOT mean Carpet Mod is installed"), `lms-paster-protocol` (Litematica Server Paster), `rei-server-protocol` (the docs say "temporarily removed" as of 1.21.4-34, but the code still has it), `chat-image-protocol`, `bladeren.protocol` (default true), `bladeren.mspt-sync-protocol`, and `protocol.strict-mode`. — [config spec](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/config-spec/leaves/en.yml); [LeavesConfig.java](https://raw.githubusercontent.com/LeavesMC/Leaves/master/leaves-server/src/main/java/org/leavesmc/leaves/LeavesConfig.java)
- JEI recipe display: open feature request #873 (2026-07-24) asks Leaves to send full recipes to the client so JEI etc. can query them again. This implies JEI recipe lookup doesn't fully work on Leaves today. — [Issue #873](https://github.com/LeavesMC/Leaves/issues/873)
- Fake players (bots): `settings.modify.fakeplayer.enable`, plus `limit`, `prefix`/`suffix`, `resident-fakeplayer`, `open-fakeplayer-inventory`, `skip-sleep-check`, `spawn-phantom`, `use-action`, `tick-type` (default NETWORK), `manual-save-and-load`, and `cache-skin`. A separate docs page covers them: `src/en/leaves/reference/fakeplayer.md`. — [config spec](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/config-spec/leaves/en.yml); [Documentation repo](https://github.com/LeavesMC/Documentation)
- Replay recording: Leaves ships a "Replay Mod API". The Lophine 26.3 tree contains a ported patch named `Leaves-Replay-Mod-API` (server and API), and the Leaves repo has a `dev/recorderapi` branch. I found no leaves.yml key for it; it's an API/command feature. — [Lophine patches](https://github.com/LophineLabs/Lophine/tree/ver/26.3/lophine-server/minecraft-patches/features); [Leaves branches](https://github.com/LeavesMC/Leaves/branches)
- Incompatible plugins listed by Leaves: **ViaVersion** (breaks mod protocols; "only translates vanilla protocols"), **AuthMeReloaded** (wrongly makes fake players log in; use AuthMeReReloaded instead), and **NoCheatPlus** ("overrides configurable fixes of Paper, causing some redstone machines to not work properly"). — [incompatible-plugins.md](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/en/leaves/reference/incompatible-plugins.md)

**Vanilla behaviour restoration [1.21.11 / docs]**
- `settings.modify.mc-technical-survival-mode` defaults to **true**. It force-overrides these settings:
  - paper-global: `unsupported-settings.allow-headless-pistons: true`, `allow-permanent-block-break-exploits: true`, `allow-piston-duplication: true`, `allow-grindstone-overstacking: true`, `packet-limiter.all-packets.max-packet-rate: 5000`, `packet-limiter.overrides: {}`, `item-validation.resolve-selectors-in-books: true`
  - paper-world: `chunks.delay-chunk-unloads-by: 0`, `entities.spawning.count-all-mobs-for-spawning: true`, `fixes.disable-unloaded-chunk-enderpearl-exploit: false`, `unsupported-settings.fix-invulnerable-end-crystal-exploit: false`
  - spigot.yml: `max-tnt-per-tick: 2000`

  In practice this restores TNT, rail and carpet duping and bedrock breaking out of the box. — [config spec](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/config-spec/leaves/en.yml)
- **Note:** that list does *not* include `allow-unsafe-end-portal-teleportation`, which is the setting Paper says controls sand/gravel duplication. — [config spec](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/config-spec/leaves/en.yml); [Paper global config](https://docs.papermc.io/paper/reference/global-configuration/)
- Update suppression: `modify.fix-update-suppression-crash` (default **true**) stops the server from crashing on update suppression. Under `modify.minecraft-old.block-updater` (all default false): `instant-block-updater-reintroduced` (locked), `cce-update-suppression`, `sound-update-suppression`, `redstone-ignore-upwards-update`, `old-block-remove-behaviour`. — [LeavesConfig.java](https://raw.githubusercontent.com/LeavesMC/Leaves/master/leaves-server/src/main/java/org/leavesmc/leaves/LeavesConfig.java)
- Other `modify.minecraft-old.*` toggles (all default false unless noted):
  - `zero-tick-plants`
  - `copper-bulb-1gt-delay`, `crafter-1gt-delay`
  - `old-hopper-suck-in-behavior`
  - `shears-in-dispenser-can-zero-amount`
  - `villager-infinite-discounts`
  - `rng-fishing`
  - `allow-grindstone-overstacking`
  - `allow-entity-portal-with-passenger` (default true)
  - `disable-gateway-portal-entity-ticking`
  - `fix-fortress-mob-spawn`
  - `revert-raid-changes.*`
  - `allow-anvil-destroy-item-entities`
  - `string-tripwire-hook-duplicate`
  
  — [config spec](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/config-spec/leaves/en.yml)
- Stackable shulker boxes: `modify.shulker-box.stackable-shulker-boxes` (older key `modify.stackable-shulker-boxes`; value 1–99 or false). Empty boxes stack on pickup, but are "not stacked in hoppers" and get split when a hopper runs, "to avoid breaking machines". — [LeavesConfig.java](https://raw.githubusercontent.com/LeavesMC/Leaves/master/leaves-server/src/main/java/org/leavesmc/leaves/LeavesConfig.java); [config spec](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/config-spec/leaves/en.yml)
- Hoppers: `fix.vanilla-hopper` (default false) "Aggressively restore hoppers to vanilla behavior… May reduce performance". An open issue (#884, 2026-08-22) still reports hopper-minecart comparator updates that differ from vanilla. — [config spec](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/config-spec/leaves/en.yml); [Issue #884](https://github.com/LeavesMC/Leaves/issues/884)
- Other technical options:
  - `use-vanilla-random` (RNG manipulation)
  - `force-void-trade`
  - `hopper-counter` (`/leaves counter`, Carpet-style)
  - `no-tnt-place-update`
  - `no-block-update-command`
  - `disable-packet-limit`
  - `redstone-shears-wrench`
  - `return-nether-portal-fix`
  - `fix.collision-behavior` (`VANILLA | PAPER`, default PAPER)
  - `fix.vanilla-portal-handle` (default true)
  - `misc` region format `linear`
  
  — [config spec](https://raw.githubusercontent.com/LeavesMC/Documentation/main/src/config-spec/leaves/en.yml); [LeavesConfig.java](https://raw.githubusercontent.com/LeavesMC/Leaves/master/leaves-server/src/main/java/org/leavesmc/leaves/LeavesConfig.java)

### Inferences
- For a 26.3 server, Leaves is **not an option right now**. Upgrading needs a three-version jump (1.21.11 → 26.1 → 26.2 → 26.3). The 26.1 PR sat unmerged for 5+ months, and the maintainers' last code activity was in August 2026. The project looks stalled, not dead.
- Leaves' defaults lean "Paper-safe" for performance. `fix.collision-behavior` defaults to PAPER, and entity activation range and the other spigot.yml optimisations aren't overridden by technical-survival mode. So even on Leaves, admins have to set spigot.yml `entity-activation-range` to 0, merge radius, and similar values by hand to approach vanilla. This is inferred from the override list above.
- Even the most feature-rich Paper fork documents residual non-vanilla behaviour: hopper fix off by default, open hopper-minecart parity bug, Paper collision default. Fabric + Carpet stays the reference for strict vanilla parity.

### Gaps
- I couldn't confirm whether the docs site's rendered config page matches the 1.21.11 code. The docs spec lags the code in places (renamed keys).
- I found no official statement from the LeavesMC maintainers on a 26.x timeline.
- I found no Leaves documentation on chunk-ticket behaviour, entity ticking, or item merging versus vanilla beyond the keys above.

## Q2. Paper itself on 26.3: vanilla deviations, restorable settings, stance, Easy Place V3

### Takeaway
Paper 26.3 is stable: build 253, 2026-11-15, channel STABLE. Paper officially says "it currently is not possible to get a 100% Vanilla experience in Paper" and that "technical players may struggle". Most exploit fixes can be reverted through `unsupported-settings`, and Paper's own vanilla guide lists the permissive values. **Plain Paper has no Easy Place V3 support.** The vanilla server code rejects use-item packets whose hit vector is more than ~1 block from the block centre, and V3 encodes block state in exactly that offset. So V3 needs a fork patch or a packet-rewriting plugin.

### Cited Findings
- Paper 26.3 latest build: `253`, time 2026-11-15T17:14:05Z, channel `STABLE`. — [fill.papermc.io](https://fill.papermc.io/v3/projects/paper/versions/26.3/builds/latest)
- Paper's vanilla guide says gameplay can differ from vanilla because of Bukkit API implementation details and bug fixes. "technical players may struggle getting their machines to work like they should", and "it currently is not possible to get a 100% Vanilla experience in Paper." — [docs.papermc.io/paper/vanilla](https://docs.papermc.io/paper/vanilla/)

**unsupported-settings in paper-global.yml.** Defaults are shown first, then the value the vanilla guide gives. [docs, version unknown, "Last updated May 12, 2025"]
- `allow-piston-duplication` false (TNT, carpet and rail duping; "does not control sand duplication")
- `allow-unsafe-end-portal-teleportation` false (enables "sand duplication"; "not recommended")
- `allow-headless-pistons` false
- `allow-permanent-block-break-exploits` false (bedrock, end portal frames)
- `skip-tripwire-hook-placement-validation` false (tripwire hook duping)
- `update-equipment-on-player-actions` true
- `oversized-item-component-sanitizer.dont-sanitize` []

The vanilla guide shows all of these at their permissive values. — [Global config](https://docs.papermc.io/paper/reference/global-configuration/); [Vanilla guide](https://docs.papermc.io/paper/vanilla/)

**Packet limiter.** The default `packet-limiter.all-packets` is 500 packets per 7 s, action KICK. The vanilla guide sets `interval: -1`. This matters for Easy Place and Litematica printer spam. — [Global config](https://docs.papermc.io/paper/reference/global-configuration/); [Vanilla guide](https://docs.papermc.io/paper/vanilla/)

**paper-world defaults vs. the vanilla-guide values**
- `chunks.delay-chunk-unloads-by` 10s → 0s
- `entities.spawning.per-player-mob-spawns` true → false (server-wide mob cap as in vanilla)
- `entities.spawning.count-all-mobs-for-spawning` false → true
- `collisions.max-entity-collisions` 8 → 2147483647
- `hopper.cooldown-when-full` true → false
- `entities.behavior.only-merge-items-horizontally` → true in the guide ("visual artifacts")
- `entities.behavior.cooldown-failed-beehive-releases` true → false
- phantom options → false
- `unsupported-settings.fix-invulnerable-end-crystal-exploit` true → false
- `misc.allow-remote-ender-dragon-respawning` → true

— [World config](https://docs.papermc.io/paper/reference/world-configuration/); [Vanilla guide](https://docs.papermc.io/paper/vanilla/)

**Other world settings**
- `misc.redstone-implementation` = `VANILLA` (default) `| EIGENCRAFT | ALTERNATE_CURRENT`. Both alternatives "change redstone dust behavior". — [World config](https://docs.papermc.io/paper/reference/world-configuration/)
- `fixes.*` defaults:
  - `falling-block-height-nerf` disabled
  - `tnt-entity-height-nerf` disabled
  - `disable-unloaded-chunk-enderpearl-exploit` false
  - `prevent-tnt-from-moving-in-water` false
  - `fix-items-merging-through-walls` false
  - `split-overstacked-loot` true
  
  `hopper.ignore-occluding-blocks` is false by default. `hopper.disable-move-event` is false; turning it on is a big performance win but breaks protection plugins. — [World config](https://docs.papermc.io/paper/reference/world-configuration/)
- `misc.update-pathfinding-on-block-update` defaults to true. — [World config](https://docs.papermc.io/paper/reference/world-configuration/)

**spigot.yml**
- The vanilla guide sets `entity-activation-range` for animals, monsters, raiders, misc, water, villagers and flying-monsters to `0` (disables throttling), and `max-tnt-per-tick: -1` (no limit). — [Vanilla guide](https://docs.papermc.io/paper/vanilla/)

**Easy Place V3 on plain Paper**
- Vanilla `ServerGamePacketListenerImpl` only accepts a use-item-on when `Math.abs(distance.x()) < 1.0000001 && …y… && …z…`, where distance is measured from the block centre. Leaves-lineage forks wrap that check with a config bypass (`needIgnoreDistance()` / `disableDistanceCheckForUseItem`). — [Lophine patch 0111 "Leaves-Alternative-block-placement-Protocol"](https://github.com/LophineLabs/Lophine/blob/ver/26.3/lophine-server/minecraft-patches/features/0111-Leaves-Alternative-block-placement-Protocol.patch); [LeavesConfig.java](https://raw.githubusercontent.com/LeavesMC/Leaves/master/leaves-server/src/main/java/org/leavesmc/leaves/LeavesConfig.java)
- An anti-cheat plugin documents how Easy Place is detected: it computes `hitVec - blockPos`. Vanilla clients stay within [0..1], while "Litematica's Easy Place exceeds >2.0". — [AntiLitematica on Hangar](https://hangar.papermc.io/ALingqing/AntiLitematica) (via search summary)
- Third-party Paper plugin docs agree. VeryMcProto says Servux's server-side EasyPlace "use[s] Mixin in the original; Paper has no Mixin runtime", so it rewrites the encoded `PLAYER_BLOCK_PLACEMENT` packet through PacketEvents. LitematicaFolia says that on Paper "the only thing your players get is Litematica's `/setblock` fallback". — [VeryMcProto Modrinth](https://modrinth.com/plugin/verymcproto); [LitematicaFolia Modrinth](https://modrinth.com/mod/litematicafolia)

### Inferences
- Plain Paper 26.3 combined with the vanilla-guide config gets close to vanilla for most farms. But sand/gravel duping still needs `allow-unsafe-end-portal-teleportation: true`, which is not in Leaves' auto-override list either. Paper also has a per-player mob cap default and spigot activation ranges to undo.
- On unmodified Paper, Easy Place V3 placements whose encoded offset exceeds ~1 block are dropped by the vanilla distance check. They are not "rewritten". Litematica then either fails to place or places the default state. V2 (Carpet accurate placement) likewise needs server-side support. This is inferred from the vanilla check and the plugin docs above; I found no Paper-maintainer statement on it.

### Gaps
- I didn't verify Paper's 26.3 handling of update suppression (whether it crashes or catches StackOverflow/CCE). No source found.
- spigot.yml `merge-radius` defaults and mob-spawn-range were not retrieved.
- The Paper docs pages carry no 26.3 version stamp. Key names could have changed in 26.x, so check against generated configs.
- I found no Paper-team statement specific to technical players beyond the vanilla page.

## Q3. Purpur, Folia and other forks on 26.3

### Takeaway
26.3 builds exist for Purpur, Folia, Leaf, DivineMC, Canvas and Lophine. **Gale stops at 26.2, Pufferfish at 1.21, Leaves at 1.21.11. Luminol's GitHub repo now returns 404.** The only 26.3 fork that targets technical play and implements Easy Place V3, Servux, Syncmatica, PCA, bots and similar is **Lophine**. But it is **Folia-based**, and both its own docs and the Luminol docs warn that Folia limits vanilla redstone parity. Leaf and DivineMC cover only part of the protocol list: no Servux, no Easy Place.

### Cited Findings
**Purpur**
- 26.3 is the current version; latest build 2659 (2026-11-16) on branch `ver/26.3`. Purpur is "designed for configurability, and new fun and exciting gameplay features" (gameplay, not technical). — [Purpur API](https://api.purpurmc.org/v2/purpur/26.3/latest); [GitHub](https://github.com/PurpurMC/Purpur)

**Folia**
- 26.3 build 8, STABLE, 2026-11-15. — [fill.papermc.io Folia](https://fill.papermc.io/v3/projects/folia/versions/26.3/builds/latest)
- Folia groups nearby chunks into independent regions, each with its own tick loop. It recommends "at least 16 cores", says "There is no more main thread", and expects "basically zero plugins that are compatible with Paper" to work unmodified. — [Folia README](https://raw.githubusercontent.com/PaperMC/Folia/ver/26.3.x/README.md)
- Luminol docs: "playing any hard vanilla-feature-related redstone machines or facilities is generally not recommendend and unsuable in Luminol". Lophine is pointed to for a better vanilla experience, "but the restoration of vanilla features is still greatly limited as folia has rewritten many of them". Folia forks are recommended only with ≥16 physical cores; otherwise use Paper or Leaf. — [Luminol docs](https://luminol-docs-neo.pages.dev/en/guide/luminol)

**Lophine (LophineLabs/Lophine)**
- Folia-based. Its README says "目标是在Folia上实现更多生电的内容（请注意，完整生电请使用Fabric）": the goal is more technical-survival content on Folia, and for full technical play you should use Fabric. Recent 26.3 releases are tags like `26.3-1e330ac` and `26.3-9c4195d` (2026-11-15). A CNB mirror serves mainland China. — [README](https://raw.githubusercontent.com/LophineLabs/Lophine/ver/26.3/README.md); [Releases](https://github.com/LophineLabs/Lophine/releases)
- The 26.3 source tree ports Leaves patches, among them:
  - Leaves Base Protocol Core, Servux Protocol, Syncmatica, BBOR, Xaero Map, **Alternative block placement (NONE/CARPET/CARPET_FIX/LITEMATICA)**
  - Fakeplayer, Replay Mod API, PCA sync, REI, Jade
  - Catch update suppression crash, CCE update suppression, Redstone ignore upwards update, Instant Block Updater, Old Block remove behaviour
  - Configurable trading with the void, Wool Hopper Counter, vanilla random
  - "Carpet features / Carpet AMS / Carpet ORG / Carpet TIS features"
  - "Restore vanilla ender pearl loading", Kaiiju "Vanilla end portal teleportation"
  
  — [Lophine 26.3 patches](https://github.com/LophineLabs/Lophine/tree/ver/26.3/lophine-server/minecraft-patches/features)
- Lophine config classes: `protocol/alternative_block_placement.enabled` (enum, default NONE). `protocol/servux` has `structure-protocol`, `hud-metadata-protocol`, `hud-logger-protocol`, `data/entity-protocol`, `data/tweaks-data-protocol`, and permission-level keys. There is also `fixes/vanilla-like-experience.enabled`. — [AlternativeBlockPlacementProtocolConfig.java](https://github.com/LophineLabs/Lophine/blob/ver/26.3/lophine-server/src/main/java/fun/bm/lophine/config/modules/function/protocol/AlternativeBlockPlacementProtocolConfig.java); [ServuxProtocolConfig.java](https://github.com/LophineLabs/Lophine/blob/ver/26.3/lophine-server/src/main/java/fun/bm/lophine/config/modules/function/protocol/ServuxProtocolConfig.java)
- Downstream: TumbleMC/Tumble, "A fork of Lophine aiming to add functions that LuminolCraft SMP needs", branch ver/26.3. — [GitHub search](https://github.com/TumbleMC/Tumble)

**Luminol**
- https://github.com/LuminolMC/Luminol returns HTTP 404 as of 2026-11-17. The LuminolMC org shows only a repo "AboutCanvas", which documents a dispute with CanvasMC over code provenance. The docs site is still up. — [LuminolMC org](https://github.com/LuminolMC); [AboutCanvas README](https://raw.githubusercontent.com/LuminolMC/AboutCanvas/main/README.md); [Luminol docs](https://luminol-docs-neo.pages.dev/en/guide/luminol)

**Leaf (Winds-Studio)**
- Release "Leaf 26.3" (tag `ver-26.3`, 2026-11-16); mcjars build #24. Described as "A Paper fork focused on finding the balance between performance, vanilla mechanics, and stability" and "performance-oriented". — [Leaf releases](https://github.com/Winds-Studio/Leaf/releases); [Leaf GitHub](https://github.com/Winds-Studio/Leaf)
- The leaf-global config lists `protocol-support` with `jade-protocol`, `appleskin-protocol`, `asteorbar-protocol`, `chatimage-protocol`, `xaero-map-protocol`, `syncmatica-protocol` (+ quota), and `do-a-barrel-roll-protocol`. It has **no Servux and no accurate/easy-place protocol**. It also has `use-vanilla-hopper: false` and `vanilla-bug-fix` toggles. [docs, version unknown] — [Leaf config docs](https://www.leafmc.one/docs/config/leaf-global)

**DivineMC (BX-Team)**
- Fork of Purpur; branch `ver/26.3`; mcjars 26.3 build #7 (2026-11-15). Features include "Regionized Chunk Ticking… similar to how Folia does it", "Parallel World Ticking", async pathfinding, mob spawning and entity tracker, and "Mod Protocols Support – Compatible with Syncmatica, Apple Skin, Jade and Xaero's Map". Easy Place and Servux are not mentioned. — [DivineMC README](https://raw.githubusercontent.com/BX-Team/DivineMC/ver/26.3/README.md); [mcjars](https://mcjars.app/api/v2/builds/DIVINEMC)

**Canvas (CraftCanvasMC)**
- Folia fork; `mcVersion = 26.3`; mcjars build #1016 (2026-11-14). Its README says the defaults aim at "Vanilla compatibility first" while it also adds region-threading changes. — [Canvas gradle.properties](https://raw.githubusercontent.com/CraftCanvasMC/Canvas/main/gradle.properties); [Canvas README](https://raw.githubusercontent.com/CraftCanvasMC/Canvas/main/README.md)

**Gale**
- "A higher-performance Paper fork without behavioral changes". Latest release `26.2-R2.3.0` (2026-07-16) and download badge "MC_26.2". **No 26.3.** — [Gale releases](https://github.com/GaleMC/Gale/releases); [Gale README](https://raw.githubusercontent.com/GaleMC/Gale/main/README.md)

**Pufferfish**
- Branches go up to `ver/1.21` only; last push 2025-12-21. **No 26.x.** — [Pufferfish branches](https://github.com/pufferfish-gg/Pufferfish/branches)

### Inferences
- **Practical shortlist for 26.3 Paper-family:**
  - (a) Plain Paper with vanilla-guide settings plus protocol plugins (Q4).
  - (b) Lophine, if the operator accepts Folia's region threading. Folia also breaks most Paper plugins and has Folia-specific redstone and chunk-loading differences. Its own docs say parity is "greatly limited".
  - (c) Wait for Leaves 26.x.
- Purpur, Leaf, DivineMC and Canvas are performance- or gameplay-oriented. DivineMC's parallel/regionized chunk ticking and async mob spawning are the kind of changes that can alter tick ordering and farm behaviour. That is an inference; I found no tests.
- For a small private server, Folia's ≥16-core recommendation and its plugin incompatibility weigh heavily against Folia-based Lophine and Canvas.

### Gaps
- Lophine's English docs and full config reference weren't found; the docs site paths returned 404.
- I found no independent test of Lophine 26.3 Easy Place V3 or of redstone parity.
- The reason Luminol's repo disappeared is unconfirmed (deleted, private, or moved).
- I didn't verify the Purpur or DivineMC config keys that touch vanilla mechanics.

## Q4. Paper plugins that implement Litematica, Servux or Easy Place protocols

### Takeaway
Several plugins bring these protocols to plain Paper. **None has a release tagged 26.3 on Modrinth as of 2026-11-17.** The newest builds target 26.2:
- **Paper Accurate Block Placement**: Easy Place V2/V3 and Tweakeroo placement.
- **VeryMcProto**: Servux, JEI, Syncmatica, Carpet subset with fake players, and EasyPlace via PacketEvents.
- **LitematicaFolia**: Servux Direct Paste and server-side .litematic paste.

### Cited Findings
- **Paper Accurate Block Placement** (hxrry27, MIT). It implements "easyPlace and accurateBlockPlacement protocols for paper based minecraft servers", including Litematica easy place and Tweakeroo flexible/accurate placement. It "supports both v2, v3 and auto" and the author recommends auto. Requirement: PacketEvents (ProtocolLib before 1.4.0). Limits: it cannot honour states Litematica never transmits, such as stacking placement (sea pickles, snow layers), redstone power level, or on/off status. Latest is 1.4.0 (2026-08-21) for **26.2**; there is no 26.3 build. — [Modrinth](https://modrinth.com/plugin/paper-accurate-block-placement); [GitHub](https://github.com/hxrry27/PaperAccurateBlockPlacement)
- **VeryMcProto** (Kevin-O-Hsu, LGPL-3.0). A "protocol-layer port" of Fabric-only server mods to a Paper plugin; it uses paperweight userdev and ships a Mojang-mapped jar.
  - Servux: "Full", meaning metadata, structures, entity/block-entity NBT, schematic paste, and fill/delete tasks.
  - JEI: full recipe sync.
  - Syncmatica: full.
  - Carpet: portable subset with `/player` fake players and `/log` HUD.
  - EasyPlace: "Implemented (needs PacketEvents)". PacketEvents rewrites the encoded `PLAYER_BLOCK_PLACEMENT` packet.
  - Explicitly **not possible**: update suppression, shulker-box stacking.
  - Builds: `26.2-b4`, `26.1.2-b8` (2026-10-19), `1.21.11-b8` (2026-10-30). No 26.3.
  
  — [Modrinth](https://modrinth.com/plugin/verymcproto); [GitHub](https://github.com/Kevin-O-Hsu/VeryMcProto)
- **LitematicaFolia** (ekaii, MIT). Server-side .litematic paste for Paper and Folia, keeping tile entities, entities and pending ticks. It also "speaks enough of the Servux wire protocol" for Litematica Direct Paste. It notes that Leaves-lineage cores (Lophine, Leaves) swallowed its `servux:*` channels until 0.5.1, when it began reclaiming them. Latest `0.8.0+26.2` and `0.4.3+26.1.2` (2026-08-29); no 26.3. — [Modrinth](https://modrinth.com/mod/litematicafolia); [Forgejo](https://forgejo.ekaii.fr/admin_ekaii/litematica-folia-ekaii)
- **Papermatica**: "fixes papermc and litematica nbt issues". Latest 1.0.5 (2026-10-03) for 1.21.6–1.21.9 only. — [Modrinth](https://modrinth.com/mod/papermatica)
- Counter-tool: **AntiLitematica** (Hangar) detects and blocks Easy Place and the printer through hit-vector checks. Its existence shows Easy Place packets are detectable and blockable at the packet level. — [Hangar](https://hangar.papermc.io/ALingqing/AntiLitematica)

### Inferences
- Plain Paper 26.3 with Paper Accurate Block Placement and PacketEvents is the lightest route to Easy Place V3. It depends on the author shipping a 26.3 build, or on the 26.2 build happening to load on 26.3; that is untested. VeryMcProto adds Servux, Syncmatica and bots, but it is NMS-bound, so its 26.2 jar is unlikely to work on 26.3 unchanged.
- Don't run these plugins on top of Leaves or Lophine. LitematicaFolia's note about channel swallowing shows the fork's built-in protocol handlers and the plugins conflict.

### Gaps
- I didn't check whether the 26.2 builds of these plugins load on Paper 26.3.
- I didn't check whether a Syncmatica-only Paper plugin exists separately.
- I didn't search Hangar exhaustively. Modrinth was queried by slug, plus one web search.

## Q5. General plugin ecosystem on 26.3 (small private server)

### Takeaway
LuckPerms, WorldEdit 7.4.6, FAWE 2.16.2, Chunky 1.5.66, BlueMap 5.29 and squaremap 1.4.3 all list 26.3 on Modrinth. **CoreProtect's latest public release, 24.1 (2026-09-24), lists only up to 26.2.** The maintainer says the codebase supports 26.3 and points to a v25 Patreon pre-compiled build. Dynmap has no 26.x release on Modrinth.

### Cited Findings
- **LuckPerms**: Modrinth versions tagged 26.3 cover bukkit, paper, folia, spigot and others. The newest is v5.5.87 (2026-10-06). — [Modrinth API](https://api.modrinth.com/v2/project/luckperms/version)
- **CoreProtect**:
  - Releases: 24.1 (2026-09-24) supports up to 26.2; 24.0 (2026-07-07) up to 26.1.2. — [Hangar API](https://hangar.papermc.io/api/v1/projects/CoreProtect/versions?limit=3); [Modrinth](https://modrinth.com/plugin/coreprotect)
  - Source: the master branch now has `PATCH_VERSION = "25.0"`, `LATEST_VERSION = "26.3"`, while the v24.1 tag has `LATEST_VERSION = "26.2"`. — [ConfigHandler.java master](https://raw.githubusercontent.com/PlayPro/CoreProtect/master/src/main/java/net/coreprotect/config/ConfigHandler.java); [v24.1](https://raw.githubusercontent.com/PlayPro/CoreProtect/v24.1/src/main/java/net/coreprotect/config/ConfigHandler.java)
  - Issue #1044 (2026-10-24), "My server is running version 26.3, and CoreProtect isn't working". Maintainer Intelli replied "Code base already has 26.3 support" and linked a Patreon post `coreprotect-v25-172388533` as "the latest pre-compiled build". — [Issue #1044](https://github.com/PlayPro/CoreProtect/issues/1044)
  - PR #1054 "Update README supported version range to 26.3" was merged 2026-11-13. PR #1051 tracks 26.3 blocks. #1023 "Cushions are not logged on Minecraft 26.3" is resolved. — [CoreProtect issues search](https://github.com/PlayPro/CoreProtect/issues?q=26.3)
- **WorldEdit**: 7.4.6 (2026-10-15) for 26.1.1–26.3 on bukkit, paper and folia. — [Modrinth](https://modrinth.com/plugin/worldedit)
- **FastAsyncWorldEdit**: 2.16.2 (2026-11-01) for 26.1.1–26.3 on paper. — [Modrinth](https://modrinth.com/plugin/fastasyncworldedit)
- **Chunky**: 1.5.66 (2026-11-04) for 26.1.1–26.3; loaders include paper and folia. — [Modrinth](https://modrinth.com/plugin/chunky)
- **BlueMap**: 5.29 (2026-10-10) for 26.1.1–26.3, with paper and spigot builds. — [Modrinth](https://modrinth.com/plugin/bluemap)
- **squaremap**: 1.4.3 has 26.3 builds (paper, folia, fabric, neoforge); 1.3.13.5 is the 26.1.2 line. — [Modrinth](https://modrinth.com/plugin/squaremap)
- **Dynmap**: latest Modrinth release v3.8 (2026-01-14) for 1.21.10/1.21.11. No 26.x listing. — [Modrinth](https://modrinth.com/plugin/dynmap)

### Inferences
- On 26.3 today, CoreProtect means either the Patreon v25 pre-compiled build or building master from source until v25 is published. This matches the reports that 24.x doesn't support 26.3.
- On 26.3, BlueMap or squaremap are safer map choices than Dynmap.

### Gaps
- Backup plugins were not researched. Running server-level tools outside the JVM (for example restic or borg snapshots) avoids plugin version dependence; this is a suggestion, not a sourced finding.
- I didn't verify what CoreProtect 24.1 actually does on 26.3 (refuses to enable vs. partial logging).
- Chinese community comparisons of Leaves vs Fabric + Carpet were not found. One search returned only generic Carpet tutorials, for example [Bilibili Carpet commands](https://www.bilibili.com/opus/688610422964617223). Lophine's README itself says full technical play needs Fabric.
