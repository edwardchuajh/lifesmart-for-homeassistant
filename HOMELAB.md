# Homelab fork

A personal fork of [MapleEve/lifesmart-for-homeassistant](https://github.com/MapleEve/lifesmart-for-homeassistant),
installed through HACS as a custom repository. Branch `homelab` is
upstream's `v2026.05.4` plus:

1. **fix(local): decode type 0x05 as a big-endian float64.** These hubs send
   battery voltages (e.g. 3.04) as `0x05` + 8 raw bytes. Upstream reads an
   extra "index" byte, which misaligns the rest of the get-config packet,
   so local mode loads no devices.
2. **fix(local): use the bare hub id as the devices' `agt`.** The login
   reply's `node_agt` is `<hub>/me`; using it gives every entity a
   different unique ID from cloud mode and breaks service calls addressed
   by hub id. `node` is the bare id. Control packets still use `node_agt`.
3. **fix(cloud): pin the API region to `cn0`.** This account's login
   returns `rgn: "tw"`, and `api.tw.ilifesmart.com` doesn't resolve.

Local mode here: hub IP, **port 8888** (the config flow defaults to 3000).

Fixes 1 and 2 are worth offering upstream; once upstream has them, move
back to upstream (keeping only fix 3, if still needed).

To pick up a new upstream release: rebase `homelab` onto the new tag,
bump `manifest.json`'s version (`vX-homelab.N`), tag it the same, and
publish a GitHub release - HACS offers releases as updates.
