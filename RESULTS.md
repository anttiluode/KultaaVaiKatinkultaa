# Results ledger — 12 November 2026

All numbers below are measured using the unchanged native V27 equations and the
600-row checkerboard splitter table, not hand-written XOR logic.

## Native logic

Four synchronous input cases, 2-tick input on each source relay's original
setpoint_mod port, with receiver beat detection on the original readout:

| Input count | XOR (-4.5,-4.5) | AND (-2.5,-2.5) | World-only (-5,+5) | Prediction-only (+5,-5) |
|---|---|---|---|---|
| 0 of 2 | 0 | 0 | 0 | 0 |
| World only | 1 | 0 | 1 | 0 |
| Prediction only | 1 | 0 | 0 | 1 |
| Both | 0 | 1 | 0 | 0 |

Receiver events occur four ticks after the source events in the tested cases.
The three-input parity prediction did **not** work in an equal-weight scan from
-14 to -1 in steps of .25. Further regimes remain possible but unproven.

## Memory write and erase

11 units: 1 world relay, 8 ring relays, 1 innovation, 1 omission.
The native ring has a preconfigured period of 32 ticks.

- Single world rhythm from empty: innovation at tick 8, prediction at tick 36,
  subsequent perfect matches require no further error events.
- Two events per lap at phases 0 and 16: both acquired.
- Complete stop after five laps: omission at 168 and old prediction stops.
- Single missed expected event: omission 168; subsequent world return rewrites
  with innovation at 200.
- A single extra phase-16 event in lap five: innovation 184; when it does not
  repeat the expected phase is erased after omission 216.
- Removed erase pathway: obsolete events continue circulating.
- Removed both write and erase pathways: initially empty memory never learns.

13 Python unit tests and native JavaScript regression checks passed in GitHub
Actions. The initial successful suite was Actions run #43187202686;
later runs repeat the tests with further diagnostics.

## Fixed-pattern stress (corrected source-versus-memory scoring)

Protocol: 33 selected phase patterns, repeated for 12 laps, score events in
the final 10 laps. This set includes fixed examples and reproducibly sampled
phase subsets, with potentially hard close-spacing cases. This is not a
representative population sample and no statistical uncertainty interval is
claimed.

| Condition | Exact patterns / 33 |
|---|---:|
| External source produces every requested event and no extra events | 20 |
| Internal prediction equals the actual external source events | 22 |
| Both source and memory are exact | 14 |

The difference matters: for [0,2] (source stimuli 2 ticks apart), source
events collapse together so the GN source relay does not deliver two separate
events. It would be misleading to call that a memory-ring error. In other
patterns the source succeeds but memory prediction misses events; both are
real, different failure modes.

Example: [0,8,16,24] produces all 40 source events in the 10 evaluated
laps, yet the ring predicts only 32 of them. This is a genuine memory failure,
not an input encoding failure.

A digital 32-position shift register is an important future baseline. The
native circuit has no proven capacity or efficiency advantage over it.

## Timing jitter

20 laps, one requested event at approximately phase 16 in each lap.
Four deterministic random phase series per jitter amplitude.

| Phase variation | Innovation spikes (range) | Omission spikes (range) |
|---|---|---|
| Exactly fixed | 1 | 0 |
| ±1 tick | 14–16 | 13–15 |
| ±2 ticks | 16–18 | 15–17 |
| ±3 ticks | 16–18 | 15–17 |

The ring reacts to normal-looking timing variation by repeatedly updating
phase-specific slots. As a template recorder it can be fast; as a rhythm
generalizer it is brittle.

Full machine-generated records are attached as the experimental-results
artifact in the GitHub Actions workflow. The deterministic stress script is
experiments/stress.py.


## Native early/late test

The original cable-delay feature (L=0 or L=1), feeding two unchanged
XOR-like receivers, can distinguish timing direction under controlled
single-beat inputs:

| World relative to prediction | World-delayed receiver | Prediction-delayed receiver |
|---|---|---|
| 1 tick early | silent | fires at t=9 |
| perfectly aligned | fires at t=10,12 | fires at t=10,12 |
| 1 tick late | fires at t=10 | silent |

Thus the *difference* between the receivers has phase-sign information,
but both receivers fire even on an exact match. This has not solved the
jitter problem. See experiments/phase.py and the GNPhase regression test.

## Scientific status

**Demonstrated within the reduced native simulator:** state-dependent
acquisition and erasure of fixed-period event slots using actual V27
setpoint-port responses and recurrent relay events, without changing weights.

**Not demonstrated:** general temporal rule learning; phase jitter tolerance;
a maximal-length native LFSR; general parity arithmetic; optical destructive
interference; biological calcium spiking; lower physical power or algorithmic
superiority.

The next experiment should attack **phase error**, not add more memory rings.
Estimate whether an observed event is early or late, then adjust a slow phase
variable instead of treating every timing variation as a new binary event.
Any improvement must be measured against unchanged GN-XOR and a simple
digital phase-tracking baseline.
