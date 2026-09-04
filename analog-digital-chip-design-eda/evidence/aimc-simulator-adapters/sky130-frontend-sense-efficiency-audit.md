# Sky130 Frontend Sense Efficiency Audit

- status: `sense_efficiency_audit_shows_transfer_plateau_before_latch_target`
- target transfer ratio: `1.000000`
- best measured transfer ratio: `0.437908`
- remaining transfer improvement: `2.28x`
- accepted post-layout evidence written: `False`

## First Principle

The comparator does not see capacitance. It sees voltage.

A frontend can add more direct sample-to-sense capacitance and still fail to give a large enough voltage if the sense node also becomes heavier. The useful question is therefore not only how much coupling was added. The useful question is how much of the sampled difference became voltage at the sense node.

In plain terms: useful coupling is the pipe that moves charge, and total sense capacitance is the bucket that charge must fill. A bigger pipe helps. A bigger bucket pushes the voltage back down. The transfer improves only when the pipe grows faster than the bucket.

## Measured Candidates

| candidate | direct sample-to-sense fF | average sense capacitance fF | direct/sense ratio | minimum transfer | remaining gap | sign cases |
|---|---:|---:|---:|---:|---:|---:|
| balanced | not extracted | 1.544460 | not extracted | 0.098039 | 10.20x | 4/4 |
| strong | 0.464290 | 2.153190 | 0.215629 | 0.372549 | 2.68x | 4/4 |
| ultra | 0.800000 | 3.292970 | 0.242942 | 0.437908 | 2.28x | 4/4 |

## What The Table Says

The balanced frontend solved the sign problem but left the signal small. Its measured transfer is about one tenth of the sampled voltage difference.

The strong frontend made the direct coupling much larger and transfer rose to about 0.37. That proved the design direction was real: moving the sampled node closer to the sense node did produce more comparator input voltage.

The ultra frontend pushed direct coupling further, to `0.8 fF`, and transfer improved again to `0.437908`. But the improvement slowed because the sense node also became larger. More of the layout is now being charged, so not every extra femtofarad of direct coupling becomes useful voltage.

## What This Means For The Next Circuit

The next circuit should not simply make the coupling plates larger again. That may keep increasing the sense-node bucket along with the pipe.

The next physical move should do one of two things:

1. reduce wasted sense capacitance while keeping direct sample-to-sense coupling high
2. add a measured preamp or buffer so the small sense voltage is amplified before latch decision

The first option is a passive layout repair. The second option spends active circuit power to buy decision margin. Both are legitimate, but they prove different things and should be measured separately.

## Claim Boundary

This audit explains why extracted frontend transfer improves slower than direct coupling and identifies the next physical design choice.

This audit does not prove latch resolution, active reset devices, comparator offset, comparator noise, DRC/LVS, SAR conversion, or accepted post-layout converter evidence.
