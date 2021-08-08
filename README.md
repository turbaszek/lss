# Launchpad Step Sequencer
[![Staic checks](https://github.com/turbaszek/lss/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/turbaszek/lss/actions/workflows/ci.yaml)

Command line tool allowing you to use
[Novation Launchpad](https://novationmusic.com/en/launch/launchpad-mini)
as a step sequencer.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
- [Launchpad Step Sequencer](#launchpad-step-sequencer)

- [How it works](#how-it-works)
- [Installation](#installation)
- [Reference](#reference)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## How it works

The `lss` handles bidirectional communication with your launchpad using MiDI protocol.
Communication is done using [mido](https://mido.readthedocs.io) (python midi wrapper).

When started `lss` creates new MiDI source named `Launchpad Step Sequencer`. This source
can be used as input in Logic Pro (or other DAW).

<p align="center"><img src="images/lss_input.png" height="200" alt="Launchpad Step Sequencer in Logic Pro"></p>
In Logic you may need to select
`Control Surfaces > Bypass All Control Surfaces` to avoid default mode of launchpad.

### Control buttons
The sequencer allows you to change tempo, mute particular instruments and reset the playhead.
<p align="center"><img src="images/lss_function_map.png" height="300" alt="Launchpad Step Sequencer in Logic Pro"></p>

### Demo
<p align="center">[<img src="images/lss_demo.png" height="300" alt="Demo video on YouTube">](https://youtu.be/1i5aPPSh9DQ)</p>

## Installation

To install locally run:
```sh
pip install -e .
```

Then start the sequencer by running
```
lss run --device-type=<DEVICE_NAME>
```
To list supported devices run:
```
lss devices list
```

## Reference

- [Novation Launchpad Mini MK3 programming guide](https://www.djshop.gr/Attachment/DownloadFile?downloadId=10737)
- [Mido documentation](https://mido.readthedocs.io)
