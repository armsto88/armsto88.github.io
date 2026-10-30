---
title: "FieldHub V2 — Sync Sweep Results"
date: 2026-10-24T20:00
date_precision: month
type: project-update
project: FieldMesh
status: published
excerpt: I ran the sync test I had planned, adding a controlled boot delay to the hub and counting how many nodes still made the sync window. Nodes were lost from a 35 s delay, and waking the hub earlier moved that edge to 70 s.
tags: [fieldhub, esp-now, sync, scaling]
highlights:
  - "Two nodes against Hub V2, with a hub boot delay injected from 0 to 85 s"
  - "Original timing: both nodes joined up to a 30 s delay, neither from 35 s"
  - "Hub woken 45 s before the slot: the edge moved to 70 s, as the timing model predicts"
  - "A missed window costs time, not data: queued readings upload at the next one"
---

In the last update I said I would test how hub boot time affects synchronisation. The test is done. I injected a controlled delay of up to 85 s before each sync window on Hub V2 and counted how many of the two nodes made it in. Each delay was sampled twice, apart from the 0 s step in the second run, whose first window wasn't logged.

With the original timing, both nodes joined at every delay up to 30 s and neither did from 35 s. That is where the timing model puts the edge. Nodes stop listening 25 s after the slot, so a hub whose boot takes longer than its wake-up lead plus 25 s misses them completely.

Waking the hub 45 s before the slot instead of 10 s, and closing the window as soon as every node has checked in, moved the edge to 70 s, again where the model predicts. Both nodes joined at every delay up to 65 s, except one step at 30 s where a node-side bug lost the window in both passes. With both nodes present a window now takes about four seconds. A missed window costs time rather than data: after four empty windows each node arrived with ten queued readings, and the hub took all twenty in under seven seconds.

![Dot plot of how many of the two nodes joined each sync window against injected hub boot delay, in two panels. With the original timing both nodes joined up to a 30 s delay and neither from 35 s. With the hub woken 45 s before the slot both nodes joined up to 65 s, except at 30 s where one pass lost one node and the other lost both because of a node-side bug, and neither joined from 70 s.](assets/project_pics/fieldmesh/fieldhub-sync-sweep.webp "Nodes that joined each sync window against injected hub boot delay, two nodes against Hub V2. Each dot is one window.")

This was two nodes in one room, with a bench hub that has no modem, so it says nothing yet about fleet size or radio contention. A later single-pass re-run put the edge in the same place. The node-side bug is fixed in the next note, but I haven't repeated the sweep since.
