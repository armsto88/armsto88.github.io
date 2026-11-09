---
title: "FieldHub — Honest Status and Faster Uploads"
date: 2026-11-07T20:00
date_precision: month
type: project-update
project: FieldMesh
status: published
excerpt: The first batch of FieldHub firmware work is done. The hub now reports what happened in each sync window, whether a deployment reached each node and how strong each node's signal is, and it uploads readings close to eight times faster.
tags: [fieldhub, firmware, uploads, status]
highlights:
  - "Hub pages show each sync window, each node's clock and the last upload, not just the serial log"
  - "A deployment shows as requested until the node confirms it, and a refusal shows as a refusal"
  - "Uploads: about 50 readings in 7.6 s, where 13 used to take about 15 s"
  - "Each node's signal strength is shown on the hub and sent to the dashboard"
---

After the sync work I spent the week making the FieldHub tell the truth. Until now most of what a hub knew about a sync window, a node's clock or an upload only appeared in its serial log. The hub's own pages now show each window, whether each node attended, whether each clock is right and how the last upload went.

Deploying a node now reports "requested" until the node actually confirms, and shows a refusal as a refusal. The setup session also survives the phone going to sleep: if no phone has been on the hub's Wi-Fi for three minutes, the hub finishes by itself, uploads, and shows the result the next time the page is opened.

Uploads were the slowest part. Dropping a time check the hub never used, and waiting for the modem's replies instead of fixed delays, cut a batch from about 15 s to a median of 4.6 s. Bigger batches then took it further: about 50 readings in 7.6 s, against about 15 s for 13 readings at the start. The hub now only moves on once the backend confirms how many readings it received, so a lost reply can no longer leave it stuck, and on a slow link it steps down to smaller batches.

Each node's signal strength in the sync window is now shown on the hub as Good, Weak or Too weak, with the figure in dBm on its detail page, and the dashboard can show the same. That has run on the bench with one hub and two nodes. A proper range test with a node on its own battery is still to do, and the pages themselves need a tidy-up on a phone.
