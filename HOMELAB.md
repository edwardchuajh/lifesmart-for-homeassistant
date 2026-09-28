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

4. **fix(local): route service calls to the hub they name.** The services
   (IR keys, scenes, press switch) are registered by whichever entry loads
   first and used that entry's connection - with one local entry per hub,
   an IR command for another hub went to the wrong hub and silently did
   nothing. Each call now uses the connection for its `agt`.

5. **fix(local): a clear error for learned IR keys by name.** Local mode
   can't send `send_ir_keys` / `send_ackeys` by key name (the hub rejects
   the RunA: `ESN1NE` for upstream's "AI_IR_<me>", `EBA` with the real
   remote id, and its irkey items expose no buttons). It now raises
   "create a LifeSmart scene for the key, then call lifesmart.trigger_scene"
   instead of reporting success while nothing happens. Hub scenes run fine
   locally (plain RunA with the scene id).
6. **fix(local): run the connection loop as a background task,** so HA's
   startup doesn't wait on it ("Setup timed out for bootstrap waiting on
   ... async_connect()").

Local mode here: hub IP, **port 8888** (the config flow defaults to 3000).

Not offered upstream for now (decided 2026-09-28). Fixes 1, 2, 4, 5 and 6 would be worth offering later; once upstream has them, move
back to upstream (keeping only fix 3, if still needed).

To pick up a new upstream release: rebase `homelab` onto the new tag,
bump `manifest.json`'s version, tag it the same, and publish a GitHub
release - HACS offers releases as updates.

**The version must be one Home Assistant can parse** (CalVer/SemVer/
PEP 440 via AwesomeVersion) or HA silently refuses to load the
integration ("Integration not found"). Use a fourth number:
`v2026.05.4.1`, `v2026.05.4.2`... - NOT `v2026.05.4-homelab.1`, which
broke the first release of this fork.
