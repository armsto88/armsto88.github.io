---
title: "FieldNode — Sweep After the Fixes"
date: 2026-11-08T21:00
date_precision: month
type: project-update
project: FieldMesh
status: published
excerpt: With all the node fixes in, I repeated the sync sweep. Both nodes now join at every delay up to 65 s, including the 30 s step that failed before, and the edge is unchanged at 70 s.
tags: [fieldnode, esp-now, sync, firmware]
highlights:
  - "Same sweep as 24 Oct, run after the node fixes and the hub changes since"
  - "The 30 s step that lost nodes before now passes in both passes"
  - "Edge unchanged at 70 s: both nodes joined up to 65 s, neither from 70 s"
  - "193 readings from each node, in order, with no gaps or duplicates"
---

Two weeks ago the sync sweep showed nodes missing windows even when the hub was on time, and I fixed the cause in the node firmware. This is the check that the fixes did what I hoped.

I ran the same sweep again on 8 November, with the current hub firmware and nodes carrying every node fix. Each delay from 0 to 85 s was run twice with both nodes present. Both nodes joined at every delay up to 65 s and neither from 70 s, so the edge is where it was. The difference is the 30 s step. It lost nodes in both passes on 24 October and now passes in both.

![Dot plot of how many of the two nodes joined each sync window against injected hub boot delay, in two panels with the same hub timing. On 24 Oct, before the node fixes, both nodes joined up to 65 s except at 30 s, where one pass lost one node and the other lost both, and neither joined from 70 s. On 8 Nov, after the node fixes, both nodes joined at every delay up to 65 s, including 30 s, and neither joined from 70 s.](assets/project_pics/fieldmesh/fieldnode-sweep-after-fixes.webp "Nodes that joined each sync window against injected hub boot delay, before and after the node fixes. Same hub timing; each dot is one window.")

Nothing was lost along the way. The hub received 193 readings from each node with consecutive sequence numbers, no gaps and no duplicates, and each node's clock was within a second of the hub's in every window.

This is still two nodes in one room on a shared battery, so it says nothing yet about larger networks or radio contention.
