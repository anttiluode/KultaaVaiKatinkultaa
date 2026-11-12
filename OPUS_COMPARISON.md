# Opus and Sol: what survives the window control?

**12 November 2026.** Source: [KultaaVaiKatinkultaaOpus](https://github.com/anttiluode/KultaaVaiKatinkultaaOpus), commit [df6d80c](https://github.com/anttiluode/KultaaVaiKatinkultaaOpus/commit/df6d80ca4166aeb9f24a62e5e4bf07949b01c314). Reproduced independently using [experiments/one_wire.py](experiments/one_wire.py) and the Opus [window.py](window.py) reference (MIT).

## The one-wire discovery

Our initial Sol architecture used two separate signed receivers for WRITE and ERASE. Opus discovered that one native XOR receiver can toggle both directions:

    World relay 0 ------- (-4.5) ----\
                                      XOR receiver 9 --- (-6) ---> ring node 3
    Memory read relay 1 - (-4.5) ----/

The ring has 8 native relays, connected by -6 edges; one full lap takes 32 ticks. The feedback reaches ring node 3 at the right time to create a missing circulating event, or suppress an existing event. The effective digital analogy under the tested synchronous schedule is:

    error = world XOR prediction
    next_ring = ring XOR error = world

The circuit never assigns a ring bit in code. The nonlinear receiver's response carries the comparison. The analogy is limited to this exact prepared timing regime.

In total there are 10 *active* nodes: one world source, eight ring relays and one XOR comparator. Opus's reference allocated a dormant eleventh node to simplify comparisons with the separate signed two-receiver circuit.

## Independent exhaustive reproduction

The resulting automated test reported:

| Implementation | Exact success cases |
|---|---:|
| Unchanged original GN27 | **255 / 255** |
| Checkerboard-free window control | **255 / 255** |

There are 255 nonempty combinations of eight binary time slots, spaced four ticks apart in a preconfigured 32-tick period. Success means the error channel was quiet after lap 8 and final-lap ring slots matched actual source-event slots.

**This test does not establish that every pattern was fully learned in one lap**. It measures successful settled behavior by lap 8, plus final memory content. A time-to-lock distribution across patterns is still worth measuring.

The earlier Sol result (14/33 end-to-end exact) was a different *circuit* and a harder *alphabet*. Some of its input patterns placed beats two ticks apart and merged in the source relay. Other failures were genuine ring errors even when the source correctly encoded four-tick-spaced events (e.g. phases 0,8,16,24). The one-wire circuit succeeding on every prepared four-tick-grid pattern is therefore a meaningful circuit improvement, not merely a change of test conditions.

## The control neuron changes the interpretation

Opus's simple window rule fires four ticks later if the sum of drives is in a fitted interval (about -13.5 to -8.4). It has neither the 600-row checkerboard table nor a 50-tick variance buffer. Yet it reproduces the entire 255-pattern result, and Opus reports it is faster.

Thus **the clean-grid XOR memory is a property of nonlinear band-pass delay circuits**, not a unique computational advantage demonstrated for GN27's geometry. This negative control deserves equal prominence to the positive result.

The simplified window model was intentionally fitted to the GN relay mode at constant 1.6. It is not an equally capable model of all GN regimes: for example it does not autonomously oscillate under constant 1.0, unlike the native clock node. This distinction still requires useful task-level demonstrations.

## The nine-relay leak and variance

Using world period 36 and events at phase 0,8,20, independent runs found 10 error events in the second half for GN27, and zero for the window control. The leak is real in this controlled simulation.

But the original variance trace recorded **zero cold-branch samples out of 14,740** after tick 100. None of 11 units crossed below the variance target (0.1) in the measured interval.

This contradicts the proposed explanation that repeated damp/amplify branch crossings caused the leak. The source of the discrepancy remains to be established. We additionally ran
[variance_branch.py](experiments/variance_branch.py): temporarily setting the
target threshold to -1 forces the damp branch while leaving the same checkerboard,
edge weights and delays. **The forced-damp network still produced 10 late
errors**, matching the unchanged GN27. The memoryless window produced zero.
Thus the particular nine-relay leak is not explained by 50-tick variance
branch switching.

The same script tested **autonomous clock behavior**: after settling,
one GN27 unit at constant 1.0 produced six beats in 360 ticks, spaced
59 ticks apart; the abstract window control produced zero. This is one
real GN-specific capability absent from the matched window neuron, although
it does not by itself establish a task-level performance benefit.

Do not call the leak biological adaptation or habituation before identifying the mechanism.

## What we keep and what we test next

1. Keep both native architectures in one repository, and let the browser lab switch between them. Use the one-wire circuit as the minimal clean-grid baseline.
2. Keep the 255/255 clean-grid score **alongside** timing jitter, off-grid inputs, source-encoding diagnostics and unknown periods. The tasks are not interchangeable.
3. Keep Opus's simple window-neuron control. Every GN-specific advantage must survive a direct comparison.
4. Determine why nine relays leak, tracing checkerboard square size, tap amplitudes, setpoint and timing, not only variance thresholds.
5. Test whether an actual slow-state mechanism can improve robustness on held-out jitter patterns without hand-snapping input phases to the ring grid.

**Proven:** native one-wire XOR feedback can acquire a prepared 8-slot rhythm, and an abstract window-neuron network can do the same. **Not proven:** new arithmetic, superior encoding, generalized rule learning, or checkerboard-specific adaptive advantage.
