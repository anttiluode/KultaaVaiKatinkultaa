"""Causal ablation: is nine-relay GN leakage caused by variance branch switching?

We *do not edit* gn27.py. Temporarily set module TARGET=-1 so any
nonnegative variance selects damp, preserving the same checkerboard sampling,
edge weights and delays. Record both native and forced-damp outcomes.
Also compare autonomous clock mode c=1.0 to Opus's memoryless window model.
"""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import gn27
from gn27 import Net,Beats,CLOCK,settle
from window import WindowNet
sys.path.insert(0,str(ROOT/"experiments"))
from one_wire import run,world_beats

def count_errors(d,ticks):
    return sum(t>=ticks//2 for t in d["error"])

def n9():
    ticks=36*40
    beats=world_beats([0,2,5],period=36,start=40,ticks=ticks)
    normal=run(beats,ticks=ticks,model="gn27",n=9,trace_var=True)
    old=gn27.TARGET
    try:
        gn27.TARGET=-1.0 # forces damp branch for all nonnegative variances
        damp=run(beats,ticks=ticks,model="gn27",n=9,trace_var=True)
    finally:
        gn27.TARGET=old
    control=run(beats,ticks=ticks,model="window",n=9)
    return {
      "native":{"late_errors":count_errors(normal,ticks),
                "variance_at_or_below_0_1":normal["variance_cold_samples"],
                "samples":normal["variance_samples"],
                "cold_per_unit":normal["variance_cold_per_node"]},
      "force_all_damp":{"late_errors":count_errors(damp,ticks),
                        "variance_at_or_below_0_1":damp["variance_cold_samples"],
                        "samples":damp["variance_samples"]},
      "simple_window":{"late_errors":count_errors(control,ticks)}
    }

def clock():
    out={}
    for model in ("gn27","window"):
        net=Net([CLOCK]) if model=="gn27" else WindowNet([CLOCK])
        if model=="gn27":net=settle(net)
        d=Beats(1)
        for t in range(360):d.see(net.step(),t)
        out[model]={"beat_count":len(d.ev[0]),"beat_ticks":d.ev[0]}
    return out

if __name__=="__main__":
    result={"nine_relay_ablation":n9(),"autonomous_clock":clock()}
    print(json.dumps(result,indent=2))
