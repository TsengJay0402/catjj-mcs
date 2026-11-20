# Copilot instructions

## Client-pack performance reminders

- When discussing a fork's client pack, shaders, or resource packs, remind the user that high-resolution textures, shaders, and distant rendering can increase hardware load. Do this when relevant to installation or selection, not during unrelated tasks.
- Read [`techsmp/client/performance-guide.md`](../techsmp/client/performance-guide.md) for the current details. Use official recommendations only; clearly distinguish Minecraft memory allocation from total system RAM.
- Distant Horizons' documented guidance suggests allocating 6–8 GB of Minecraft RAM on 4–8-core CPUs and 12–16 GB on 10+ core CPUs. These are troubleshooting suggestions, not minimum PC requirements.
- ModernArch v4.7.2 128x is about 255 MB, but its official page does not publish minimum PC requirements. Do not invent hardware requirements for it or other packs/shaders; say when official specs are unavailable.
- Keep performance advice in agent replies and project documentation. Do not set `RESOURCE_PACK_PROMPT` / `resource-pack-prompt` for this warning, because that text appears in the server resource-pack prompt when players connect. Keep the resource pack optional (`RESOURCE_PACK_ENFORCE=false`) unless the user asks otherwise.
