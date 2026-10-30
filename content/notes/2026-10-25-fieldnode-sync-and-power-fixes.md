---
title: "FieldNode — Sync and Power-Off Fixes"
date: 2026-10-25T21:00
date_precision: month
type: project-update
project: FieldMesh
status: published
excerpt: The sync sweep showed nodes missing windows even when the hub was on time. The cause was in the node firmware, and fixing it became a set of small changes, each checked on the bench before the next.
tags: [fieldnode, firmware, sync, power]
highlights:
  - "Readings now sit on a fixed UTC clock grid, so nodes no longer drift into the sync window together"
  - "An alarm that comes due during a wake is now handled, not wiped"
  - "A node never powers off over a pending RTC alarm"
  - "A node that loses its clock listens for the hub in short bursts and recovers by itself"
---

After each reading a node set its next wake for one interval from now, so every wake drifted later by the length of the wake. Nodes released by the same sync window drifted together. When a reading was still running at the pre-wake minute of the next sync, the node skipped that window completely and powered off with its radio never switched on.

The fix went in as seven small changes, each checked on the bench before the next:

- Readings are scheduled on the UTC clock grid, so all nodes sample in the same minute and nothing drifts.
- An alarm that comes due while a node is awake is handled before it sleeps, instead of being cleared.
- A node never releases power over a pending RTC alarm. On the V3 board a set alarm can hold the power switch on, which used to leave the node awake and doing nothing.
- A node that loses its clock listens for the hub for 4 s of every 45 s, then recovers its time from the next window. Before, it stayed awake with its radio off until the battery was flat.
- A node removed from a hub stays on the radio for its idle period instead of cutting power at once.
- A queued time update is aged by however long it waited before it is applied.
- Daily sync mode is removed, so the interval is the only schedule.
