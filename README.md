# Kultaa vai katinkultaa? — Gold or fool's gold?

A **real, falsifiable GN experiment**: can the same unchanged nonlinear Geometric Neuron serve as a clock, relay, memory, signed discrepancy detector, and native write/erase circuit?

**Main finding (12 November 2026):** In a precisely synchronized 32-tick scaffold, 11 unmodified V27 units can acquire and remove circulating prediction events using their own error spikes. The network does not run a programmed XOR, does not directly assign stored bits, does not update weights, and does not learn the period.

[Interactive offline lab](index.html) | [Scientific analysis](SCIENCE.md) | [Measured limits](RESULTS.md) | [Python experiments](experiments/kultaa.py) | [Stress diagnostics](experiments/stress.py) | [Automated checks](.github/workflows/ci.yml)

## Native signed discrepancy

The same native receiver at Constant Signal 1.6 changes its logic by changing only two input edge weights.

| World | Prediction | XOR (-4.5,-4.5) | AND (-2.5,-2.5) | Innovation (-5,+5) | Omission (+5,-5) |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 1 | 0 | 1 | 0 |
| 0 | 1 | 1 | 0 | 0 | 1 |
| 1 | 1 | 0 | 1 | 0 | 0 |

Every source and receiver runs the original 4-tick, 50-sample-variance V27 checkerboard feedback equations. Source inputs are -10 for two ticks on the native setpoint_mod port. No output override or explicit Boolean comparison exists in the neuron.

**Precision:** this table is for **synchronous two-tick events**. A one-tick input offset can destroy XOR cancellation.

## New: Opus's one-wire XOR baseline

We independently reproduced the [Opus repository](https://github.com/anttiluode/KultaaVaiKatinkultaaOpus) using our unchanged GN27 core. **One unsigned XOR receiver, fed back to memory node 3 with weight -6, both writes and erases**. A missing beat is written; a false existing beat is removed by the same error pulse. This makes the separate innovation/omission pair optional for a fixed synchronized binary rhythm.

**Exhaustive 8-slot test:** 255/255 nonempty 4-tick-grid rhythms eventually acquired with zero late error pulses, both on GN27 and on Opus's checkerboard-free window-neuron control. The criterion is error silence after lap 8 plus a final-lap exact match, *not* proof every pattern locks in one lap.

**GN-only distinction:** the nine-relay 36-tick ring produced 10 late errors under GN27 but zero under the window control; all 14,740 measured late variance values were above the 0.1 branch boundary. Forcing every unit to remain on the damp branch still gave 10 errors, disproving the proposed variance-branch-switch explanation for that leak. An isolated GN27 clock at constant 1.0 fired six times in 360 ticks (59-tick intervals); the window control never fired.

[Read the full Opus/Sol reconciliation](OPUS_COMPARISON.md), [reproduce the exhaustive comparison](experiments/one_wire.py), or [test the causal branch ablation](experiments/variance_branch.py).

In the offline browser lab, use **Native feedback circuit** to switch between the older signed-two-receiver model and the new one-wire XOR architecture.

## Eleven units: memory that edits itself by pulses

The fixed circuit has:

- node 0: incoming world event relay
- nodes 1..8: eight relays joined in a one-way circulating ring, edge weight -6
- node 9: innovation (world present, memory absent) with incoming weights -5,+5
- node 10: omission (memory present, world absent) with incoming weights +5,-5
- node 9 -> ring node 3, weight -6: write
- node 10 -> ring node 3, weight +6: erase

An initially empty ring exposed to a 32-tick world rhythm yields:

    world beat        t = 4
    innovation beat   t = 8
    ring-node-3 beat  t = 12
    ring prediction   t = 36
    subsequent errors none (perfectly periodic world)

Why node 3? Eight four-tick relay hops make one 32-tick lap. The error response is delayed, but the write position is chosen so the newly circulating event reaches the prediction outlet at the *next* expected occurrence.

The input and gate weights are hand-selected. The event written into the ring is created through GN dynamics; experiment code never edits a memory array.

## The key experiments

| Condition | Native result |
|---|---|
| One 32-tick beat, ring initially empty | One innovation spike, then replay and silence |
| Two beats per lap at phases 0 and 16 | Both positions are acquired |
| World stops after five laps | One omission spike; obsolete circulating event disappears |
| One expected world event missing for a lap | Omission erases; restored world triggers rewrite |
| One unexpected world event in an empty time slot | Innovation writes; later omission erases it |
| A second persistent event starts after lap five | Its phase is acquired while old phase continues |
| No feedback wires | Memory remains empty; innovation continues indefinitely |
| Write-only, no erase feedback | Obsolete predictions are not removed |

All these scenarios are in tests/test_kultaa.py. Python and JavaScript native logic and memory tests run in GitHub Actions.

## Where the gold is not yet

The fixed-period scaffold is strong enough for clean periodic events but is sensitive to phase jitter. Experiments/stress.py distinguishes source relay failure from memory prediction failure for denser rhythms, and tests ±1 to ±3 ticks of variation.

**Not proved:**
- learning the period of an unknown sequence
- general three-input parity or computing in arithmetic modulo 2
- robust phase-locked adaptation to early and late events
- a full-period LFSR or Berlekamp–Massey-style learning of feedback taps
- physical destructive interference, biological dendritic calcium channels, or reduced hardware power
- superiority over a digital cyclic shift register

The three-input equal-weight sweep from -14 to -1 in increments of .25 found **no** full 0,1,0,1 parity response. The sampled nonlinear response has a firing band; that alone is not a periodic activation function.


**Stress result:** In 33 deliberately selected patterns, 20/33 were encoded exactly by the source, 22/33 were predicted exactly from actual source events, and 14/33 succeeded end-to-end. With ±1 tick of jitter, the two error receivers produced repeated updates (14–16 innovations and 13–15 omissions over 20 laps) instead of settling. See RESULTS.md for protocols and limitations.

**Early/late probe:** Two 1-tick cable-offset comparators encode timing direction: one channel fires for early, the other for late. But with perfectly aligned input, both channels fire; an additional common-mode suppression mechanism is required. See experiments/phase.py and its regression test.

Read SCIENCE.md for detailed comparison to Gidon 2020, Keller 2012, Pyragas feedback control, Jeffress coincidence detection and Massey's feedback-register synthesis.

## Reproduce

Python 3.11+ with NumPy; Node.js 22+ optional; browser entirely offline.

    pip install -r requirements.txt
    python -m unittest discover -s tests -p 'test_*.py' -v
    python experiments/kultaa.py --output results/latest.json
    python experiments/stress.py results/stress.json
    node tests/test_native.cjs

Open index.html from disk (or enable GitHub Pages) for the animated ring and event raster. Controls let you choose world schedules and turn native write and erase feedback on/off.

The GitHub Actions workflow runs the tests and provides the full generated JSON as an artifact.

## Original source and lineage

- [PerceptionLab](https://github.com/anttiluode/PerceptionLab) — original accidental ecg.json feedback graph
- [GeometricNeuronOriginReview](https://github.com/anttiluode/GeometricNeuronOriginReview) — original graph autopsy
- [GeometricNeuronSurfaceListener / V26](https://github.com/anttiluode/GeometricNeuronSurfaceListener) — native setpoint-modulation port and two-source cancellation
- [GeometricNeuronV27](https://github.com/anttiluode/GeometricNeuronV27) — native relays, 32-tick ring, the 4-tick pipeline and original splitter samples
- [GN-XOR](https://github.com/anttiluode/GN-XOR) — native XOR and initial world-versus-replay mismatch
- **KultaaVaiKatinkultaa** — signed innovation/omission pair feeding persistent ring state

The files gn27.py, v27.js, taps.json and taps.js are copied unchanged from GN-XOR, originally from V27, under the MIT license. This repo adds only experiment wiring, controls, observation code, tests, docs and the offline page.

**What would make it a scientific discovery rather than an attractive demo?** A novel and independently replicated functional capability beyond ordinary delay-line memory and nonlinear gates, measured against equally small standard baselines under previously unseen event streams. We have not reached that bar. The experiment makes it possible to find out.
