---
title: "FieldHub V2 — Scaling the Network"
date: 2026-10-23T14:00
date_precision: month
type: project-update
project: FieldMesh
status: published
excerpt: With the core hardware coming through bring-up, I’ve started looking more closely at how FieldMesh behaves as the network grows.
tags: [fieldhub, esp-now, sync, scaling]
highlights:
  - "First test: controlled hub boot delays, two nodes against Hub V2"
  - "Goal: measured node capacity instead of theoretical estimates"
---

The first test will examine the timing between the hub and multiple wireless nodes. Earlier field data suggests hub boot time can reduce the overlap available for synchronisation, so I’ll test this directly by injecting controlled boot delays while running two nodes against the new Hub V2 hardware.

The goal is to replace theoretical node-capacity estimates with measured behaviour before scaling the system further.
