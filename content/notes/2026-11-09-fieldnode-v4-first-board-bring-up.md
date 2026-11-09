---
title: "FieldNode V4 — First Board Bring-Up"
date: 2026-11-09T20:00
date_precision: month
type: project-update
project: FieldMesh
status: published
excerpt: The first FieldNode V4 boards arrived on 6 November. The first one has been through the bring-up suite: the power rails, RTC wake cycles and I²C ports all behave as designed, and the SDI-12 and RS-485 interfaces pass their first checks.
tags: [fieldnode, hardware, bring-up, v4]
highlights:
  - "From a 4.14 V battery the 3.3 V, 5 V and 12 V rails measure 3.31 V, 5.05 V and 12.14 V"
  - "25 consecutive RTC wake cycles pass, and the battery reads within about 1% of a meter"
  - "All four I²C ports read an SHT40 cleanly, and the selectable 3.3, 5 and 12 V port supply is right on a meter"
  - "Still to do: reed input, real sensors on SDI-12 and RS-485, sleep current"
---

The first FieldNode V4 boards arrived on 6 November, so last month's PCB design is now hardware. I adapted the bring-up suite I used for the FieldHub and ran the first board through it, powered from a single battery cell.

The rails came up as designed. With the battery at 4.14 V the 3.3 V, 5 V and 12 V rails measured 3.31 V, 5.05 V and 12.14 V, and the battery reading was within about 1% of a meter. The wake path works too: all 11 RTC alarm checks and 25 consecutive wake cycles passed, and the board cuts its own power within 0.1 s of releasing it. All four I²C ports read an SHT40 moved between them with no bus errors, the ADC passes its checks, and the selectable analogue-port supply gives the right 3.3, 5 or 12 V on a meter.

Some of the board is still unproven. The reed input needs a connector I don't have yet, and the SDI-12 and RS-485 ports have only passed their checks with nothing attached. I haven't measured sleep current either, because I don't have a suitable meter. Real sensors are next, starting with a soil probe on the analogue inputs.
