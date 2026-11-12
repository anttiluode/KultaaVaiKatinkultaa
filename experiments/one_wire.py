"""Independent re-check of the Opus one-wire toggle memory and its window control.

Source idea: https://github.com/anttiluode/KultaaVaiKatinkultaaOpus
Based on e4_selfring.py, e5_stress.py, e6_control.py (2026-11-12).
GN27 is imported unchanged; window.py was copied unchanged from Opus.

For each 4-tick-aligned world event the native unit receives a two-tick
-10 pulse at its setpoint port. The event/prediction/error are measured from
the units' own threshold crossings, never from an explicit logic calculation.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from gn27 import Net, Beats, RELAY, settle
from window import WindowNet

def build(model="gn27", n=8):
    """One world input, n native ring cells, one XOR, one feedback wire."""
    if n < 3:
        raise ValueError("n must be >=3")
    edges=[(1+i,1+(i+1)%n,-6.0,0) for i in range(n)]
    comparator=n+1
    edges += [(0,comparator,-4.5,0),(1,comparator,-4.5,0)]
    edges += [(comparator,3,-6.0,0)]  # delay-compensated feedback address
    cls=Net if model=="gn27" else WindowNet if model=="window" else None
    if cls is None: raise ValueError(model)
    net=cls([RELAY]*(n+2),edges)
    return (settle(net) if model=="gn27" else net),comparator

def world_beats(slots,period=32,start=40,ticks=640):
    """Nominal beat *times*, not setpoint pulse times."""
    beats=[]
    for lap in range((ticks-start)//period+2):
        for s in slots:
            t=start+lap*period+4*s
            if 4<=t<ticks:
                beats.append(t)
    return beats

def run(beats,ticks=640,model="gn27",n=8,trace_var=False):
    net,error=build(model,n)
    det=Beats(net.n)
    pulses=set()
    for beat in beats:
        pulses.update((beat-4,beat-3))
    below=0
    sampled=0
    per_node_below=[0]*net.n
    for t in range(ticks):
        sp=np.zeros(net.n)
        if t in pulses: sp[0]=-10.0
        det.see(net.step(sp_ext=sp),t)
        if trace_var and model=="gn27" and t>=100:
            cold=(net.var<=0.1)
            below+=int(np.count_nonzero(cold))
            sampled+=net.n
            for i in np.flatnonzero(cold):per_node_below[int(i)]+=1
    report={"world":det.ev[0],"prediction":det.ev[1],"error":det.ev[error],
            "error_node":error,"ring":{str(i):det.ev[i] for i in range(1,n+1)}}
    if trace_var and model=="gn27":
        report["variance_cold_samples"]=below
        report["variance_samples"]=sampled
        report["variance_cold_per_node"]=per_node_below
    return report

def late_success(result,period,ticks,quiet_after_lap=8):
    last_lap=ticks//period-1
    extract=lambda ev: sorted({(x%period)//4 for x in ev if x//period==last_lap})
    # Compare only quantized output slots; error *pulses* must cease late.
    return (sum(x>=quiet_after_lap*period for x in result["error"])==0
            and extract(result["world"])==extract(result["prediction"]))

def exhaustive(model="gn27",ticks=640):
    success=[]
    failed=[]
    for mask in range(1,256):
        slots=[i for i in range(8) if mask & (1<<i)]
        d=run(world_beats(slots,ticks=ticks),ticks,model)
        (success if late_success(d,32,ticks) else failed).append(mask)
    return {"model":model,"tested":255,"passed":len(success),
            "failed_masks":failed,"criteria":"zero error pulses after lap 8; final world/prediction slots equal",
            "protocol":"n=8, lap=32 ticks, 4-tick aligned slots, starts at world beat t=40"}

def compare_nine_ring(model,trace_var=False):
    ticks=40*36
    beats=world_beats([0,2,5],period=36,start=40,ticks=ticks)
    d=run(beats,ticks=ticks,model=model,n=9,trace_var=trace_var)
    return {"model":model,
            "errors_in_second_half":sum(t>=ticks//2 for t in d["error"]),
            "total_errors":len(d["error"]),
            "last_errors":d["error"][-25:],
            **{k:v for k,v in d.items() if k.startswith("variance_")}}

def compare_switch(model="gn27"):
    ticks=32*30
    a=world_beats([0,3,5],start=40,ticks=15*32)
    b=world_beats([1,6],start=15*32+8,ticks=ticks)
    d=run(a+b,ticks=ticks,model=model)
    return {"model":model,
            "late_errors":sum(t>=18*32 for t in d["error"]),
            "predicted_last_lap":sorted({(t%32)//4 for t in d["prediction"] if t//32==29}),
            "world_last_lap":sorted({(t%32)//4 for t in d["world"] if t//32==29})}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--exhaustive",action="store_true")
    parser.add_argument("--output",default="-")
    args=parser.parse_args()
    report={"one_wire_single":{m:run(world_beats([0],ticks=32*12),ticks=32*12,model=m)
                               for m in ("gn27","window")},
            "switch":{m:compare_switch(m) for m in ("gn27","window")},
            "nine_relay_comparison":{m:compare_nine_ring(m,trace_var=(m=="gn27"))
                                     for m in ("gn27","window")}}
    if args.exhaustive:
        report["exhaustive"]={m:exhaustive(m) for m in ("gn27","window")}
    data=json.dumps(report,indent=2)
    if args.output=="-": print(data)
    else:
        dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(data+"\n")
        print("Wrote",dest)
    for model in ("gn27","window"):
        x=report["nine_relay_comparison"][model]
        print("NINE_RING",model,"late errors",x["errors_in_second_half"],file=sys.stderr)
    if args.exhaustive:
        for m,s in report["exhaustive"].items():
            print("EXHAUSTIVE",m,s["passed"],"/",s["tested"],file=sys.stderr)
if __name__=="__main__":main()
