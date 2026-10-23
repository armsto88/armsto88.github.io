---
title: "FieldHub V2 — Sensor Bring-Up"
date: 2026-10-23T15:00
date_precision: month
type: project-update
project: FieldMesh
status: published
excerpt: The latest FieldHub V2 prototype is now well into bench bring-up.
tags: [fieldhub, bring-up, i2c, adc]
image: assets/project_pics/fieldmesh/fieldhub-v2-top-800.webp
image_alt: Render of the FieldHub V2 circuit board
highlights:
  - Four I²C sensor ports verified with an SHT40, including at 400 kHz
  - ADS1015 inputs within about 1% of a reference meter, no crosstalk
  - "Reed input works, but its GPIO moves in the next revision"
  - "Still to test: ESP-NOW, RTC backup retention, longer wake cycles"
---

The four external I²C sensor ports have been verified with an SHT40, including operation at 400 kHz. The ADS1015 analogue inputs are also working across all four channels, with measurements within about 1% of my reference meter and no observed crosstalk.

The reed-switch input works functionally, but testing confirmed that the current GPIO choice is susceptible to interference from Wi-Fi and ADC activity. That will be corrected in the next revision.

A few tests remain, including ESP-NOW communication, RTC backup retention and longer wake-cycle testing.
