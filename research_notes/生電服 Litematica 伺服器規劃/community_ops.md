# 生電服 community practice and operations (itzg/minecraft-server, MC Java 26.3), as of 2026-11-17

Research date: 2026-11-17. Live data came from the Modrinth API, the Leaves API, PyPI, the GitHub API and the itzg/MCDR docs, all queried today. Search-snippet-only claims are flagged.

## 1. Server software consensus: Fabric + Carpet (+ TIS Addition) vs Leaves vs Paper

### Takeaway
For a 26.3 生電服 the decision is effectively already made. Leaves has **no 26.x build at all** (its newest release is 1.21.11, last pushed 2026-08-13). The Fabric technical stack (Carpet, Carpet TIS Addition, Servux, Syncmatica, Litematica, Lithium, Ledger, FabricProxy-Lite, pca-protocol) **all have 26.3 releases**. Community consensus has long been Fabric + Carpet for "really technical" playerbases. Leaves is the "Paper but more vanilla, plus plugins" option, and Paper itself breaks technical mechanics.

### Cited Findings
- The Leaves download API lists versions only up to `1.21.11`, with no 26.x entry. Builds for 1.21.11 are 152–157. — [Leaves API v2 projects/leaves](https://api.leavesmc.org/v2/projects/leaves); [builds for 1.21.11](https://api.leavesmc.org/v2/projects/leaves/versions/1.21.11)
- The newest LeavesMC/Leaves GitHub releases are `1.21.11-157-a8bb272` (2026-08-13) and 1.21.11-156 / 155 (2026-07-20). The repo was last pushed 2026-08-13, and the branches list has no 26.x branch (`dev/1.21.11` is the newest). — [GitHub API releases](https://api.github.com/repos/LeavesMC/Leaves/releases); [repo](https://github.com/LeavesMC/Leaves)
- Leaves has a PR "升级到 26.1（测试）" (#846, opened 2026-04-21) and a PR "更新 26.1.2" (#863, opened 2026-06-03). Issue #871 "我们需要26.1和26.2" (2026-07-17) was closed by pointing to #863, with no timeline given. I could not confirm the merge state of #863 because of GitHub API rate limits, but no 26.x build has been published. — [Issue #871](https://github.com/LeavesMC/Leaves/issues/871); [PR #863](https://github.com/LeavesMC/Leaves/pull/863); [PR #846](https://github.com/LeavesMC/Leaves/pull/846)
- Leaves describes itself as a "Fork of Paper aimed at repairing broken vanilla properties." — [GitHub LeavesMC/Leaves](https://github.com/LeavesMC/Leaves)
- Leaves configuration exposes a lot of technical-client protocol support:
  - `syncmatica:enable` (with quota), `pca:pca-sync-protocol`
  - `servux:structure-protocol` / `entity-protocol` / `hud-metadata-protocol`
  - `litematics-protocol`, `alternative-block-placement` (default NONE), `bbor-protocol`, `jade-protocol`, `xaero-map-protocol`, `leaves-carpet-support`, `lms-paster-protocol`, `rei-server-protocol`
  - **all default false/off**, so each one has to be enabled.

  It also has a built-in fakeplayer (`/bot`, `limit` 10, `use-action`, `resident-fakeplayer`) and a `minecraft-old` section of opt-in old/vanilla behaviours: `cce-update-suppression`, `instant-block-updater-reintroduced`, `zero-tick-plants`, `string-tripwire-hook-duplicate`, `old-hopper-suck-in-behavior` and others. — [Leaves configuration reference](https://docs.leavesmc.org/leaves/reference/configuration)
- KLPBBS official Leaves thread (posted 2024-08-23):
  - Leaves aims to repair vanilla features broken by Paper ("服务端皆在修复被 Paper 破坏的原版特性").
  - Carpet support is described as only "部分功能集成，特别支持假人关键特性" (partially integrated, with specific support for key fake-player features).
  - Syncmatica is called fully compatible, and MiniHUD/BBOR/Jade/Xaero are supported.
  - It also adds non-vanilla gameplay tweaks (no anvil "too expensive" limit, protection-enchant stacking, infinity+mending), which are departures from vanilla.

  — [KLPBBS: Leaves - 原版特性的生电服务端](https://klpbbs.com/thread-146096-1-1.html)
- Public Leaves 生電 servers advertising on MineBBS are on **1.21.11** (e.g., "1.21.11｜纯公益｜Leaves端｜原版特性｜养老生电"). — [MineBBS thread](https://www.minebbs.com/threads/leaves.47640/)
- r/admincraft discussion:
  - Paper fixes bugs that technical players rely on and adds limits such as packet-rate limits, and it changes redstone update order and how entities pass through nether portals.
  - The thread recommends Paper/Purpur for regular servers and Fabric for "really technical playerbases", and "If you want Paper but even more vanilla, check out Leaves".
  - A later thread says farms and storage systems rely on precise vanilla mechanics, which "Fabric & lithium correctly preserve".

  (Search-result summary; mirror domain.) — [r/admincraft mirror 2025-02-12](https://reddit.birdcat.cafe/r/admincraft/comments/1inuzw9/is_paper_better_than_fabric_optimization_mods_for); [r/admincraft mirror 2025-04-12](https://reddit.birdcat.cafe/r/admincraft/comments/1jx9xdm/where_do_most_servers_go_wrong/mmtm83d/?context=3)
- Chinese tutorials consistently define the 生電服 stack as Fabric server core + Carpet + MCDR, with a Velocity proxy for mirror/creative sub-servers:
  - aimerny's 4-part tutorial: Fabric 模组服 / Velocity 群组服 / MCDR 端
  - Bilibili "[MCDR生电服手册]"
  - Zhihu "MC生电服开服教程"

  Most of these are 2023–2024 and 1.20.x-era. — [aimerny tutorial (1) 引言](https://aimerny.top/2023/09/25/mcdr/mcdr-tutor-1-pre/); [aimerny (2) Fabric](https://aimerny.github.io/2023/09/26/mcdr/mcdr-tutor-2-fabric/index.html); [Bilibili BV1Mq4y167cF](https://www.bilibili.com/video/BV1Mq4y167cF/); [知乎 p/653816975](https://zhuanlan.zhihu.com/p/653816975)
- A Bilibili 专栏 calls Carpet "以fabric作为服务器核心的技术生存类服务器常用模组" (the mod commonly used by Fabric-core technical survival servers). — [Bilibili cv17831706](https://www.bilibili.com/read/cv17831706/) (search snippet)
- **Fabric stack availability on 26.3 (Modrinth API, game_versions=26.3, loader=fabric, queried 2026-11-17):**

  | Project | Newest 26.3 version | Published |
  |---|---|---|
  | Carpet (`carpet`) | `26.3` | 2026-09-18 |
  | Carpet TIS Addition | `v1.83.3-mc26.3` (five 26.3 builds since v1.83.x) | 2026-11-14 |
  | Servux | `0.12.2` | 2026-09-27 |
  | Litematica | `0.29.1` | 2026-09-27 |
  | Syncmatica | `0.3.20` | 2026-09-22 |
  | Fabric API | `0.166.2+26.3` | 2026-11-11 |
  | Lithium | `mc26.3-0.26.3-fabric` | 2026-10-28 |
  | Ledger | `1.3.25` | 2026-10-04 |
  | FabricProxy-Lite | `v2.12.0` (covers 26.1.1–26.3) | 2026-03-28 |
  | pca-protocol (Fallen-Breath's server-only PCA fork) | supports 26.3 | — |
  | Carpet Org Addition | lists 26.3 | — |
  | **Carpet Extra** | **no 26.3 build; newest listed is 26.2** | — |

  — [Modrinth API carpet](https://api.modrinth.com/v2/project/carpet/version?game_versions=%5B%2226.3%22%5D&loaders=%5B%22fabric%22%5D); [carpet-tis-addition](https://modrinth.com/mod/carpet-tis-addition/versions); [servux](https://modrinth.com/mod/servux); [litematica](https://modrinth.com/mod/litematica); [syncmatica](https://modrinth.com/mod/syncmatica); [fabric-api](https://modrinth.com/mod/fabric-api); [lithium](https://modrinth.com/mod/lithium); [ledger](https://modrinth.com/mod/ledger); [fabricproxy-lite](https://modrinth.com/mod/fabricproxy-lite); [pca-protocol](https://modrinth.com/mod/pca-protocol) / [source](https://github.com/Fallen-Breath/pca-protocol); [carpet-extra](https://modrinth.com/mod/carpet-extra); [carpet-org-addition](https://modrinth.com/mod/carpet-org-addition)
- The original `plusls-carpet-addition` slug does not resolve on Modrinth. The maintained server-side PCA protocol provider is `pca-protocol`, described as "A fork of plusls-carpet-addition, provides PCA protocol support to the server only". — [Modrinth pca-protocol](https://modrinth.com/mod/pca-protocol)
- Litematica Easy Place V3 server support: Servux 0.3.7's changelog added "V3 Easy Place Protocol support for Litematica and Tweakeroo" without requiring Carpet Extra, and recommends turning off the Carpet(-Extra) accurate-placement rule when Servux is used. (Search snippet only. The direct Modrinth version page returned 404 today.) — [Modrinth servux 0.3.7 (via search)](https://modrinth.com/mod/servux/version/0.3.7)

### Inferences
- On 26.3 the only real choice is **Fabric + Carpet + Carpet TIS Addition + Servux** (Servux supplies Easy Place V3, entity/block-entity data and structure boxes) **+ Syncmatica + pca-protocol + Lithium + Ledger**. Leaves would force staying on 1.21.11. Paper is widely reported to alter technical mechanics.
- Carpet Extra has no 26.3 build. That matters less for Easy Place than it used to, because V3 goes through Servux, not Carpet Extra's `accurateBlockPlacement` (V2). Carpet Extra-only rules (e.g., dispenser behaviours) are unavailable until it updates.
- Typical reasons people pick Leaves: they want Bukkit plugins (LuckPerms, CoreProtect, chat bridges and the like) while keeping 生電 behaviours and fake players, with protocol toggles for client mods. Reported/derivable pitfalls:
  - Behaviour is opt-in config, not vanilla parity by default.
  - Carpet support is partial.
  - It changes some vanilla gameplay.
  - **It lags updates**: as of Nov 2026 it is still on 1.21.11 while vanilla is on 26.3.

### Gaps
- Could not fetch r/technicalminecraft or the Carpet Discord FAQ directly. Reddit mirrors were unreachable and the Bilibili opus hit a captcha. No primary SciCraft/Hekate/Mythic statement of server software was retrieved. (Widely known that SciCraft uses Fabric + Carpet, but **unverified here**.)
- No sourced list of concrete Leaves protocol bugs (e.g., Syncmatica/Servux desyncs) was found.
- Could not confirm the merge state of Leaves PR #863 (GitHub rate-limited).
- Carpet TIS Addition's EOL page (fetched today) lists 26.1–26.1.2 and 26.2 as actively supported, but does not yet list 26.3 even though 26.3 builds exist on Modrinth. — [carpet.tis.world/eol](https://carpet.tis.world/eol)

## 2. MCDReforged (MCDR): plugins, 26.x compatibility, Docker

### Takeaway
MCDR is a Python wrapper. It runs the server as a child process and parses console output; it does not modify the server. The current version is **v2.16.3 (2026-11-10)** and it is actively maintained. **itzg/minecraft-server has no built-in MCDR support.** The options are:
- the official `mcdreforged/mcdreforged-<jdk>` images, which run the server jar yourself without itzg's auto-install;
- a tiny community image (`notevenaneko/mcdr-docker`) that layers MCDR on top of itzg;
- skipping MCDR and using itzg-native features (rcon, mc-backup).

### Cited Findings
- MCDR does not need to modify the server and adds management via plugins; Python is its dependency. — [aimerny tutorial (4) MCDR](https://aimerny.github.io/2023/09/26/mcdr/mcdr-tutor-4-mcdr/index.html)
- Latest MCDR on PyPI is `2.16.3`, uploaded 2026-11-10. — [PyPI mcdreforged](https://pypi.org/project/mcdreforged/)
- Recent release notes:
  - v2.16.0 (2026-09-19): plugin metadata schema v1, `AsyncRconConnection`, improved RCON retry, and the `environment`/`environment_inherit` server process env controls.
  - v2.16.2 (2026-10-22): rebuilt the docker image for the eMudhra intermediate CA compromise and advises pip >= 26.2.2 and certifi >= 2026.10.19.
  - v2.16.3 (2026-11-10): fixed invalid PyPI links in the pim install summary.

  — [MCDR GitHub releases](https://github.com/MCDReforged/MCDReforged/releases)
- Official MCDR Docker images:
  - `mcdreforged/mcdreforged` (base), `mcdreforged/mcdreforged-extra`, and `mcdreforged/mcdreforged-{temurin (suggested), corretto, zulu}`.
  - Java 8/17/21/25 are available (default 21) via the `-jdk25` suffix.
  - Workdir is `/mcdr`; mount the server folder there. Examples use `docker run -it`.
  - "you need to install the dependencies/runtime required for running the server", so use a JDK image.
  - No compose example is provided.

  — [MCDR docs: Docker](https://docs.mcdreforged.com/en/latest/docker.html); [Docker Hub mcdreforged](https://hub.docker.com/r/mcdreforged)
- Community itzg+MCDR image `notevenaneko/mcdr-docker` (repo Cattttttttt/mcdr-docker):
  - Built on itzg/docker-minecraft-server: `/data` is the MC server, `/mcdr` holds MCDR config/plugins.
  - Maps itzg `TYPE=FABRIC`/`VANILLA` to MCDR `vanilla_handler`.
  - Needs `stdin_open: true` + `tty: true` (or `disable_console_thread: true`). Env: `MCDR_VERSION` (2.x only), `EULA`, `UID`/`GID`.
  - Warns it has no automated tests and that some itzg env vars may behave differently. 2 stars, 16 commits.

  — [GitHub Cattttttttt/mcdr-docker](https://github.com/Cattttttttt/mcdr-docker)
- Server type for 26.3 Fabric: with MCDR you set `handler: vanilla_handler`. The image above maps FABRIC to vanilla_handler. — [GitHub Cattttttttt/mcdr-docker](https://github.com/Cattttttttt/mcdr-docker)
- MCDR Plugin Catalogue entries (meta.json fetched 2026-11-17):

  | Plugin ID | Version | Description |
  |---|---|---|
  | `prime_backup` | 1.14.0 | "A powerful backup plugin for MCDR, an advanced backup solution for your Minecraft world" |
  | `quick_backup_multi` | 1.10.1 | multi-slot backup/restore |
  | `where_is` | 2.2.2 | query players' coordinates |
  | `here` | 1.2.2 | broadcast position + highlight |
  | `location_marker` | 1.3.3 | server-side waypoint manager |
  | `bot` | 1.3.1 | "The best carpet bot manager!" |
  | `advanced_calculator` | 0.3.2 | in-game calculations |
  | `mirror_server_reforged` | 1.0.8 | reforged MCDR-Mirror-Server |

  `seen` and `calc` IDs were not found under those names. — [PluginCatalogue meta branch e.g. prime_backup](https://raw.githubusercontent.com/MCDReforged/PluginCatalogue/meta/prime_backup/meta.json); [catalogue site](https://mcdreforged.com/en/plugins)

### Inferences
- **MCDR on 26.3:** MCDR parses vanilla-format log lines, and Fabric 26.3 logs in vanilla format, so `vanilla_handler` should work. No 26.x-specific breakage report was found. Treat this as likely, not verified.
- **Docker trade-off:**
  - With itzg, you get auto-download of Fabric, `MODRINTH_PROJECTS`, `VERSION` management, rcon-cli and the mc-backup sidecar, but no MCDR.
  - With the official MCDR image, you get MCDR plugins (Prime Backup in-game `!!pb` rollback, `!!bot`, `!!here`, mirror sync) but must manage the server jar/mods yourself, e.g., install Fabric via fabric-installer into `/mcdr/server`.
  - The community hybrid image is low-maturity (2 stars, no tests). A pragmatic split for 4–8 friends is itzg for the server plus mc-backup, using Carpet `/player` directly. Use MCDR (official image) only if in-game backup/rollback commands and bot management are wanted.

### Gaps
- No primary statement on MCDR + Minecraft 26.x log-format compatibility was found.
- The plugin catalogue's per-plugin MCDR version requirements were not checked.
- Docs for the mirror_server_reforged config were not fetched.

## 3. itzg/minecraft-server specifics for a Fabric 26.3 technical server

### Takeaway
Use `TYPE=FABRIC`, `VERSION=26.3`, optionally pinning `FABRIC_LOADER_VERSION`, and load mods via `MODRINTH_PROJECTS` with `MODRINTH_DOWNLOAD_DEPENDENCIES=required`. **There is no `TYPE=LEAVES`.** The image's deploy scripts include Paper/Purpur/Pufferfish/Leaf/Folia/Canyon and others but not Leaves, so Leaves would need `TYPE=CUSTOM` (and there is no 26.3 Leaves anyway). Since MC 1.21.2, itzg recommends the native `pause-when-empty-seconds` over its own autopause. Memory: set `MEMORY` (heap) and leave about 25% extra container headroom.

### Cited Findings
- **`TYPE=FABRIC` variables:**
  - `VERSION`: defaults to the latest vanilla release.
  - `FABRIC_LOADER_VERSION`, `FABRIC_LAUNCHER_VERSION`: pin versions, otherwise the latest is used.
  - `FABRIC_META_BASE_URL`, `FABRIC_LAUNCHER`, `FABRIC_LAUNCHER_URL`, `FABRIC_FORCE_REINSTALL`.
  - The docs note "most mods will require the Fabric API mod", installable via `MODRINTH_PROJECTS=fabric-api`.

  — [itzg docs: Fabric](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/server-types/fabric/)
- **`MODRINTH_PROJECTS`:**
  - Comma/newline list. Entry forms are `project`, `project:version` (a version ID overrides MC/loader compatibility checks), `project:release|beta|alpha`, a `+` suffix for "most stable", prefixes `datapack:`/`fabric:`/`forge:`/`paper:`, and `@/path/listing.txt` (with `#` comments).
  - A trailing `?` marks a project optional, so it logs a warning instead of failing startup.
  - `MODRINTH_DOWNLOAD_DEPENDENCIES`: `none` (default) / `required` / `optional`.
  - `MODRINTH_PROJECTS_DEFAULT_VERSION_TYPE`: `release` (default) / `beta` (release + beta) / `alpha`.
  - `MODRINTH_LOADER` is for custom servers.

  — [itzg docs: Modrinth](https://docker-minecraft-server.readthedocs.io/en/latest/mods-and-plugins/modrinth/)
- **Paper-family types documented:** PAPER (`PAPER_BUILD`, `PAPER_CHANNEL`), PUFFERFISH, PURPUR, LEAF (`LEAF_BUILD`), FOLIA. Leaves is not documented. — [itzg docs: Paper](https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/server-types/paper/)
- **The image's `scripts/` directory** has `start-deployFabric`, `start-deployLeaf`, `start-deployCanyon`, `start-deployPaper`, `start-deployPurpur`, `start-deployFolia`, `start-deployCustom` and others, but **no `start-deployLeaves`**. — [GitHub itzg/docker-minecraft-server scripts](https://github.com/itzg/docker-minecraft-server/tree/master/scripts)
- Latest itzg image release is `2026.11.0` (2026-11-09). — [GitHub releases](https://github.com/itzg/docker-minecraft-server/releases)
- **Auto-pause:**
  - "As of 1.21.2 it is not recommend to use this feature since Minecraft server natively auto-pauses when the server is empty. That is configured via … `PAUSE_WHEN_EMPTY_SECONDS`, which maps to the `pause-when-empty-seconds` server property."
  - Legacy `ENABLE_AUTOPAUSE` requires `MAX_TICK_TIME=-1`, plus `AUTOPAUSE_TIMEOUT_EST` (default 3600), `AUTOPAUSE_TIMEOUT_INIT` (600), `AUTOPAUSE_KNOCK_INTERFACE` (eth0), and `.skip-pause`.

  — [itzg docs: autopause](https://github.com/itzg/docker-minecraft-server/blob/master/docs/misc/autopause-autostop/autopause.md)
- **JVM/memory:**
  - `MEMORY` (default `1G`) sets Xms and Xmx; `INIT_MEMORY`/`MAX_MEMORY` set them separately, and `%` values are allowed. Leaving it empty makes the JVM use 25% of the container limit.
  - "Memory resource requests and limits on the overall container should also account for non-heap memory usage. An extra 25% is a general best practice."
  - `USE_AIKAR_FLAGS=true` (adjusted when MEMORY ≥ 12G), `USE_MEOWICE_FLAGS`, `USE_MEOWICE_GRAALVM_FLAGS`, `JVM_OPTS`, `JVM_XX_OPTS`.

  — [itzg docs: JVM options](https://docker-minecraft-server.readthedocs.io/en/latest/configuration/jvm-options/)
- **Spawn chunks:**
  - Spawn chunks were **removed in Java 1.21.9** (snapshot 25w31a: "Removed spawn chunks and the `spawnChunkRadius` gamerule").
  - `spawnChunkRadius` had been added in 1.20.5 (24w03a, default shrunk to 3×3).
  - From 1.21.9 onward, use `/forceload` "if necessary".

  — [Minecraft Wiki: Spawn chunks](https://minecraft.wiki/w/Spawn_chunks)
- Carpet 26.1 release notes mention fake-player fixes and elytra flight for fake players. Carpet 26.1 betas switched to Java 25. — [Modrinth Carpet 26.1](https://modrinth.com/mod/carpet/version/26.1); [Carpet 26.1-beta-1](https://modrinth.com/mod/carpet/version/26.1-beta-1) (search summary)
- Frostor's Carpet Addition for 26.3 requires Java 25. That is consistent with 26.x needing Java 25. (Search summary.) — [moddex frostors-carpet-addition](https://moddex.gg/mod/frostors-carpet-addition)

### Inferences
- A suggested `environment` block (not tested):

  ```yaml
  TYPE: FABRIC
  VERSION: "26.3"
  MEMORY: 10G
  USE_MEOWICE_FLAGS: "true"   # or USE_AIKAR_FLAGS
  MODRINTH_DOWNLOAD_DEPENDENCIES: required
  MODRINTH_PROJECTS: |
    fabric-api
    carpet
    carpet-tis-addition
    servux
    syncmatica
    pca-protocol
    lithium
    ledger
  ```

  - Set the container `mem_limit` to about 12.5–13G.
  - Keep `ENABLE_RCON` (default on in itzg) for mc-backup.
  - Use an image tag with Java 25 (`latest`/`java25`), since 26.x needs Java 25. Verify the tag name separately.
- **Pause when empty:** for a technical server with chunk-loaded farms that should keep running while nobody is online (via Carpet bots or `/forceload`), set `PAUSE_WHEN_EMPTY_SECONDS=0` (or negative) to disable native pausing. Otherwise the whole server freezes when empty. The default value and the disable semantics were **not verified in this research**; check the server.properties docs.
- **No spawn chunks since 1.21.9:** all permanent chunk loading on 26.3 comes from players, Carpet fake players (`/player <name> spawn`), `/forceload`, or mechanics such as portals and ender pearls. The ender pearl/portal loading mechanics were not verified here. This changes classic designs that relied on spawn-chunk storage and farms.
- **View/simulation distance:** no sourced 生電-specific recommendation was found. A common choice for 4–8 players on a 12-core host is view-distance 10–12 and simulation-distance 10–12. Many farms (perimeters, mob farms) are designed around simulation distance, so pick one value and keep it stable. This is unsourced.
- **Memory:** 8–12 GB heap is ample for 4–8 players; 125 GB RAM is not a constraint. This is unsourced; the only sourced guidance is the 25% overhead rule.

### Gaps
- itzg Java-25 image tag naming and default for VERSION=26.3 were not fetched.
- The rcon docs page was not fetched; itzg enables rcon by default per general knowledge.
- No sourced technical-community view-distance/simulation-distance numbers.

## 4. Backups/rollback and survival + creative/mirror topology with Velocity

### Takeaway
The standard 生電 topology is **survival (main) + mirror (镜像服, periodic copy of the survival world) + creative (创造服)** behind **Velocity**. Each Fabric backend runs **FabricProxy-Lite** with modern forwarding, and players switch with `/server`. For backups:
- with itzg, use the **itzg/mc-backup** sidecar (tar/rsync/restic/rclone over rcon `save-off`/`save-all`);
- with MCDR, use **Prime Backup**;
- add **Ledger** (Fabric, 26.3 available) for block-level grief/accident rollback. CoreProtect is Bukkit-only, so it is only relevant on Leaves/Paper.

### Cited Findings
- **Velocity sub-server layout** (aimerny tutorial):
  - Sub-servers `main` (25565), `mirror` (25566), `crea` (25567), with `try = [main, mirror]`.
  - FabricProxy-Lite goes on each Fabric backend; direct connections then fail, which is "正常的".
  - `player-info-forwarding-mode = "modern"`, and Velocity's `forwarding.secret` is copied to `secret` in `FabricProxy-Lite.toml`.
  - Players switch with `/server <name>`.

  The tutorial does not cover client mods over the proxy. — [aimerny tutorial (3) Velocity](https://aimerny.github.io/2023/09/26/mcdr/mcdr-tutor-3-velocity/index.html)
- Chinese 生電 tutorials describe "镜像服""创造服" sub-servers switched via commands, using Velocity, with FabricProxy-Lite required on Fabric. — [aimerny tutorial (1)](https://aimerny.top/2023/09/25/mcdr/mcdr-tutor-1-pre/); [Bilibili Velocity 群组端 video](https://www.bilibili.com/video/av591721417/?p=5)
- **FabricProxy-Lite README:**
  - "only support velocity and using Fabric-API handle velocity packet."
  - Config/env: `hackOnlineMode` (`FABRIC_PROXY_HACK_ONLINE_MODE`, default true), `hackEarlySend` (needed for e.g. LuckPerms), `hackMessageChain` (fixes "Received chat packet with missing or invalid signature" when switching servers), `disconnectMessage`, and `secret` / `FABRIC_PROXY_SECRET` / `FABRIC_PROXY_SECRET_FILE` (required).
  - Setup steps: set Velocity `player-info-forwarding-mode` to `modern` and match the secret.

  — [GitHub OKTW-Network/FabricProxy-Lite](https://github.com/OKTW-Network/FabricProxy-Lite)
- FabricProxy-Lite v2.12.0 supports 26.1.1–26.3. — [Modrinth fabricproxy-lite](https://modrinth.com/mod/fabricproxy-lite)
- The Velocity project explicitly does not support proxy chaining (Velocity behind BungeeCord/Velocity). — [PaperMC Velocity docs (security)](https://docs.papermc.io/velocity/security) (search summary)
- **itzg/mc-backup sidecar:**
  - `BACKUP_METHOD` = `tar` (default) / `rsync` / `restic` / `rclone`.
  - `BACKUP_INTERVAL` (default 24h, sleep syntax such as "2h 30m"), `INITIAL_DELAY` (2m), `BACKUP_ON_STARTUP` (true), `PAUSE_IF_NO_PLAYERS` (false).
  - `PRUNE_BACKUPS_DAYS` (7), `PRUNE_BACKUPS_COUNT` (tar/rsync).
  - `RCON_HOST`, `SRC_DIR=/data`, `DEST_DIR=/backups`, `EXCLUDES` (default `*.jar,cache,logs,*.tmp`), `CRON_SCHEDULE` (overrides interval settings), `TAR_COMPRESS_METHOD` (zstd and others).
  - restic needs a fixed container hostname.

  — [GitHub itzg/docker-mc-backup README](https://github.com/itzg/docker-mc-backup)
- **MCDR backup and mirror plugins:** Prime Backup 1.14.0 ("advanced backup solution"), QuickBackupM 1.10.1 (multi-slot backup/restore), and Mirror Server Reforged 1.0.8 for syncing survival to a mirror. — [PluginCatalogue prime_backup](https://raw.githubusercontent.com/MCDReforged/PluginCatalogue/meta/prime_backup/meta.json); [quick_backup_multi](https://raw.githubusercontent.com/MCDReforged/PluginCatalogue/meta/quick_backup_multi/meta.json); [mirror_server_reforged](https://raw.githubusercontent.com/MCDReforged/PluginCatalogue/meta/mirror_server_reforged/meta.json)
- Ledger (Fabric block logging/rollback) has 26.3 releases (1.3.25, 2026-10-04). — [Modrinth ledger](https://modrinth.com/mod/ledger)

### Inferences
- **Proxy necessity:** with Tailscale and only 4–8 players, a Velocity proxy is optional. A creative server can simply run on another port (e.g., `host:25566`) without a proxy, which avoids FabricProxy-Lite and modern-forwarding complexity and any risk to client-mod custom payloads.
  - Velocity forwards unknown plugin-message channels between client and backend in general, so Servux/Syncmatica/PCA should work through it. **No source confirming Servux/Syncmatica/PCA over Velocity on 26.x was found**, so test before relying on it.
  - With Velocity, enable `hackMessageChain` to avoid chat-signature kicks on server switch.
- **Mirror without MCDR:** under itzg, a mirror can be refreshed by a host cron job that copies the latest mc-backup archive (or an rsync of `/data/world`) into the creative/mirror container's volume while that container is stopped.
- **Backup cadence:** world snapshots via mc-backup (e.g., every 2–6 h, rsync/restic for dedup) handle disasters and machine-explosion rollbacks. Ledger handles targeted rollback of accidental block changes without a full world revert. This split is a common pattern but is unsourced here.

### Gaps
- No source on Syncmatica/Servux/PCA/Litematica Easy Place V3 behaviour through Velocity + FabricProxy-Lite on 26.x.
- No Velocity build/version check for 26.3 was done (it has to support the 26.3 protocol).
- No primary source documenting the "survival + creative mirror" practice at named servers (TIS etc.); only tutorials.

## 5. Version strategy: stay on 1.21.x or move to 26.x?

### Takeaway
The ecosystem has split:
- The **Fabric technical mod stack has caught up to 26.3**: Carpet in Sept 2026, TIS Addition through Nov 2026, Servux/Litematica/Syncmatica in Sept 2026.
- **Carpet Extra (26.2 max) and Leaves (1.21.11 max) have not.**
- **Carpet TIS Addition designates 1.21.11 as a Long Term Support version**, which signals that the TIS community treats 1.21.11 as a durable "stay" version.
- Public Leaves 生電 servers still run 1.21.11.
- 26.4 is in snapshots (26.4-snapshot-8 on 2026-11-10).

### Cited Findings
- The Carpet TIS Addition EOL page lists LTS for 1.14.4, 1.15.2, 1.16.4/5, 1.17.1, 1.18.2, 1.19.4, 1.20.1, 1.20.5/6, 1.21/1.21.1 and **1.21.11**. Versions 26.1–26.1.2 and 26.2 are "To be determined" (depending on the release schedule). 26.3 is not yet on the page. — [carpet.tis.world/eol](https://carpet.tis.world/eol)
- Modrinth game-version tags: 26.3 released 2026-09-15 (rc-1 2026-09-10); 26.4-snapshot-1 to snapshot-8 between 2026-09-22 and 2026-11-10. — [Modrinth API tag/game_version](https://api.modrinth.com/v2/tag/game_version)
- Carpet TIS Addition has shipped five 26.3 builds (v1.83.x), the latest being v1.83.3-mc26.3 on 2026-11-14. — [Modrinth carpet-tis-addition versions](https://modrinth.com/mod/carpet-tis-addition/versions)
- Leaves is still on 1.21.11 and users are filing "we need 26.1 and 26.2" requests. — [Leaves issue #871](https://github.com/LeavesMC/Leaves/issues/871); [Leaves API](https://api.leavesmc.org/v2/projects/leaves)
- Paper already has 26.3 builds (26.3, 26.3-rc-3), so the Paper upstream is not what's blocking Leaves. — [PaperMC Fill API v3](https://fill.papermc.io/v3/projects/paper)
- Spawn chunks and `spawnChunkRadius` were removed in 1.21.9. This was a major technical-play change before the 26.x numbering. — [Minecraft Wiki: Spawn chunks](https://minecraft.wiki/w/Spawn_chunks)

### Inferences
- For a **new** 26.3 world prioritizing Litematica Easy Place V3, the required mods exist: Litematica 0.29.x client, Servux 0.12.x server, Carpet 26.3 and TIS Addition. Moving to 26.3 is viable. The cost is losing Carpet Extra rules (until it updates) and any Leaves/Bukkit-plugin path.
- Staying on 1.21.11 is the conservative choice the TIS LTS designation supports. Any decision to stay should weigh client-side mod availability (Litematica/Tweakeroo/MiniHUD for 1.21.11 remain available), but that wasn't checked here.

### Gaps
- No community discussion (Bilibili/知乎/Reddit) of specific 26.1–26.3 redstone or technical mechanic changes was retrieved. Searches returned only mod changelogs. A redstone experimental-features or update-order change list for 26.x is **not covered**.
- No survey of which named technical servers (TIS, SciCraft, Hekate, Mythic) currently run which version was found.
