# Scientific analysis — what did we actually build?

**Date:** 12 November 2026. **Implementation:** unchanged V27 numerical model.
**Interpretation:** a fixed nonlinear substrate whose effective memory changes through
feedback events, without conventional training or direct manipulation of stored bits.

## The dynamical unit

The 2025 Perception Lab loop was reduced in the V26/V27 lineage to a 4-tick
pipeline, fixed checkerboard splitter samples, and a 50-sample variance-regulated
coupler. The original model code and tap data are retained unchanged at the root.

Let B_j(t) be the sum of two beat wires from another unit, and let u_i(t) be an
external setpoint-port stimulus. The receiver's setpoint is

    S_i(t) = 0.5 + 0.1 * (1.6 + Σ_j weight_ij * B_j(t) + u_i(t))

The rest of the unit retains its original nonlinear damp/amplify update, checkerboard
sampling and delayed feedback. An observed beat is the first tick its own sampled
readout exceeds 3, after a previously quiet tick.

The 1.6 relay receives a 2-tick -10 input through the native port and beats
approximately four ticks later in the tested settled setting. During a beat, the
source's wire sum is around 2. This makes signed weight choices physically
meaningful without inventing a Boolean gate inside the neuron.

## A setpoint band is not a general modular arithmetic unit

- Two equal -4.5 edges: one input drives the unit into its effective firing
  region; two simultaneous inputs overshoot it, giving synchronous XOR-like
  behavior. No opposite-signed weights are required for this particular gate.
- Two equal -2.5 edges: one signal is too weak, two reach the active region,
  giving AND-like behavior.
- (-5,+5): the world event alone can excite, a matching predicted event
  cancels the setpoint excursion, and a prediction alone is silent.
- (+5,-5): the inverse, responding to a prediction that world does not support.

**Critical correction to a tempting explanation:** the two same-sign inputs
do *not* destructively interfere as independently propagating coherent waves.
The model adds real-valued source readouts and passes their sum through a
non-monotonic response, with a discretized checkerboard sampling function.
No independently measured complex phase cancellation was shown.

A three-input equal-weight sweep of -14 to -1 in 0.25 increments did not
produce full 3-bit parity (response counts 0,1,2,3 = 0,1,0,1).
This does not exclude other weights, state histories or time-dependent gates,
but it directly contradicts the easy claim that the receiver must be a
general addition-modulo-2 element.

## Signed surprise becomes a native memory-editing signal

Circuit indices: node 0 world, nodes 1..8 a one-way ring, node 9 innovation,
node 10 omission. Ring edge weight -6; 4 ticks per relay; total 32 ticks per lap.

Receivers:

    world (0) -5 ----> innovation (9) <---- +5 prediction (1)
    world (0) +5 ----> omission  (10) <---- -5 prediction (1)

Feedback:

    innovation (9) -6 ----> memory node 3
    omission  (10) +6 ----> memory node 3

Nothing assigns values to ring memory directly. The only external influences
are the world source's -10, 2-tick setpoint pulses and an optional one-time
initial seed for control experiments.

Why node 3? When world at tick 4 is unpredicted, innovation fires at tick 8.
It excites node 3 at tick 12, then six further 4-tick relay hops bring the
event back to prediction node 1 at tick 36 (the next expected 32-tick period).
For a predicted world omission, the positive error feedback reaches node 3
at the *same moment* as the expected traveling ring wave and can suppress it.

This is a **temporal address implemented by physical connectivity**.
The negative-error circuit makes erasure direction-specific and avoids the
flaw of the naive unsigned XOR feedback, which wrote even when a predicted
event was absent from the world.

### Demonstrations and controls

See experiments/kultaa.py and tests/test_kultaa.py:
- Empty ring exposed to one 32-tick world beat: one innovation beat; future
  predictions arise from ring dynamics.
- Two separate phases (0,16) in the same 32-tick lap are acquired.
- A world rhythm stops after lap 5: a native omission event erases the old
  phase; continued spurious predictions are prevented.
- Single omission: briefly erased then re-written when world returns.
- Single extra: temporarily written then erased.
- **Control without feedback**: error pulses continue and the ring stays empty.
- **Control without erase feedback**: obsolete predictions persist.

The ring does **not** learn an arbitrary period. Its 32 ticks are built into the
prepared eight-hop topology. Tests of dense patterns and phase jitter are
recorded by experiments/stress.py. Successful learning here is acquisition
and removal of periodic positions in a pre-existing temporal scaffold, not
learning a general rule or modifying the network's synaptic weights.

## Five connections to science, and what they do not prove

**Gidon et al. (Science, 2020):** Human layer 2/3 cortical neurons have
dendritic calcium spikes with non-monotonic input-response curves; such
curves can support computations analogous to XOR. Functional resemblance
does not validate this artificial checkerboard model as ion-channel
neurophysiology.
https://doi.org/10.1126/science.aax6239

**Keller, Bonhoeffer and Hübener (Neuron, 2012):** Mismatch responses were
observed in primary visual cortex when locomotion-predicted visual feedback
and actual visual flow diverged. The GN circuit compares an explicitly
prepared repeating event template with world-event input; it has not
learned a visual model or motor prediction.
https://doi.org/10.1016/j.neuron.2012.03.040

**Pyragas delayed-feedback control:** A continuous difference between
current and time-delayed state can vanish on a target periodic orbit.
Our two event streams also silence a discrepancy receiver on a match,
but we have NOT shown that the GN feedback stabilizes unstable orbits
or shares the mathematical conditions of Pyragas control.
https://pmc.ncbi.nlm.nih.gov/articles/PMC4893174/

**Jeffress coincidence-detection models:** Neural delay lines and
coincidence detection can convert relative timing into a spatial response.
GN's one-tick sensitivity is related to timing-selective coincidence,
but NOT evidence of robust real-world microsecond sound localization.

**Berlekamp–Massey / LFSRs:** The Massey 1969 synthesis algorithm finds
a shortest *linear feedback shift register* for a supplied sequence by
updating feedback coefficients based on discrepancies. Here the wiring
is held fixed, so no feedback polynomial is being learned. A maximal
length 2^n-1 requires a suitable synchronous GF(2) register and primitive
feedback polynomial; an eight-node GN relay loop does not imply 255
states. These claims require separate constructive tests.
https://crypto.stanford.edu/~mironov/cs359/massey.pdf

## Things this does not establish

1. **No new mathematical XOR principle.** AND/XOR from non-monotone
   transfer functions are widely known.
2. **No general self-organization of topology.** Couplings, port choice,
   ring period and write-node address were selected by the experimenter.
3. **No lossless world compression in the observed time series.** The
   identity world = prediction XOR residual applies to aligned binary
   variables; the physical receiver can fail under jitter and colliding
   events. Retaining an incomplete residual would not be invertible.
4. **No Kolmogorov complexity measurement.** Length of this prepared
   ring is not a bound on the shortest description of arbitrary input,
   much less a direct measurement of incomputable complexity.
5. **No energy advantage.** The error receivers may remain silent when
   predictions match but the rest of the ring continues switching.
   CPU/GPU consumption and physical switching energy were not compared.
6. **No clinical or industrial safety claim.** Rhythmic anomaly
   detection would need stringent sensitivity/specificity validation.

## Most valuable next tests

- Test arbitrary multi-beat patterns at denser spacing and phase jitter,
  compared against a digital shift-register baseline under the same budget.
- Let a fixed ring acquire several distinct stable slots, and erase exactly
  one without altering the others.
- Add two offset receivers to determine *signed early versus late* timing
  and use the sign for a phase-correction feedback experiment.
- Investigate whether changing ring connectivity through native error
  events can learn a **generative rule**, not merely remember phases.
- Only then test a native LFSR; demand the full distinct-state cycle and
  check the known primitive polynomial baseline.
- Compare original archived Perception Lab graph with this reduced
  node implementation to verify the behavior survives the reduction.

## Scientific contribution if replicated externally

What may be distinctive is the **reuse of one accidental, unchanged,
non-monotonic dynamical substrate** for clock, relay, memory, signed
discrepancy, and temporary state rewriting. That is an implementation
and design result, not yet a claim of a novel scientific principle or
superior algorithm. The first job of this repository is to test its
range honestly and make its failure modes visible.
