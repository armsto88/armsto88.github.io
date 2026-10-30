---
title: "Auris — Choosing Parts for the Audio Front End"
date: 2026-10-25T19:00
date_precision: month
type: project-update
project: Auris
status: published
excerpt: Every part in the Auris audio front end now has an exact part number, and the passives were chosen for what they do to the signal. Ceramic capacitors, for example, can turn enclosure vibration into noise.
tags: [auris, acoustics, audio, hardware]
highlights:
  - "Every fitted part in the audio front end has an exact LCSC part number, test pads aside"
  - "Signal-path capacitors are C0G, and bias and DC-blocking capacitors are tantalum"
  - "One ceramic that didn't belong on a bias node was caught and replaced"
  - "Next: the same check for the power and LTE sections"
---

The audio front end is the first part of Auris to reach exact part numbers. Every fitted component now has a specific LCSC part, apart from the test pads, which are bare copper. The guide's build stops if one is missing, so the parts list and the design can't drift apart.

Picking the parts meant checking each passive against what it does in the signal path. Class II ceramic capacitors (X5R, X7R) are piezoelectric, so on a high-impedance bias node, wind or rain vibration on the enclosure can show up as signal. The signal-path capacitors are therefore C0G, and the bias and DC-blocking capacitors are tantalum. The mic-bias filter moved from "tantalum or polymer" to a tantalum part, because polymer capacitors leak more and that leakage would add noise to the bias. Where no DC flows, as in the ADC input series resistors, thick film does the job. Thin film stays on the resistors that carry DC or set the gain.

The check also caught one of my own mistakes. The preamp mid-rail capacitor was listed as a ceramic, which is exactly what the reasoning above rules out, and it is now tantalum.

The power and LTE sections get the same check next.
