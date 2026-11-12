"""Native signed surprise and error-driven circulating memory.

This is an experiment using gn27.Net unchanged. No direct bit edits, forced
output, or programmed XOR/AND in the native unit.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from gn27 import Net,Beats,RELAY,settle

PERIOD=32

def logic(flags,weights,lags=None):
    n=len(flags)+1
    if lags is None: lags=[0]*len(flags)
    net=settle(Net([RELAY]*n,[(i,n-1,float(w),0) for i,w in enumerate(weights)]))
    det=Beats(n)
    for t in range(44):
        sp=np.zeros(n)
        for i,(present,lag) in enumerate(zip(flags,lags)):
            if present and lag<=t<lag+2: sp[i]=-10
        det.see(net.step(sp_ext=sp),t)
    return det.ev

def truth(weights):
    return {f"{a}{b}":logic((a,b),weights)[-1] for a,b in ((0,0),(1,0),(0,1),(1,1))}

def parity_scan():
    out=[]
    for wt in np.arange(-14.0,-0.99,0.25):
        bits=[]
        for n in range(4):
            ev=logic([1]*n+[0]*(3-n),[wt]*3)[-1]
            bits.append(int(bool(ev)))
        out.append({"weight":float(wt),"response_0_1_2_3_inputs":bits})
    return out

def graph(write=True,erase=True):
    edges=[(i+1,1+(i+1)%8,-6.0,0) for i in range(8)]
    edges += [(0,9,-5.0,0),(1,9,+5.0,0),(0,10,+5.0,0),(1,10,-5.0,0)]
    if write: edges.append((9,3,-6.0,0))
    if erase: edges.append((10,3,+6.0,0))
    return edges

def learn(schedule,seed=False,write=True,erase=True,ring=False):
    """schedule has one iterable of world-event start phases (0..31) per lap.
    External event stimuli enter a real setpoint port; state is never assigned.
    """
    net=settle(Net([RELAY]*11,graph(write,erase)))
    det=Beats(11)
    for t in range(len(schedule)*PERIOD):
        lap,slot=divmod(t,PERIOD)
        sp=np.zeros(11)
        if seed and t<2: sp[1]=-10
        if any(0<=slot-p<2 for p in schedule[lap]): sp[0]=-10
        det.see(net.step(sp_ext=sp),t)
    out={"world":det.ev[0],"prediction":det.ev[1],
         "innovation":det.ev[9],"omission":det.ev[10]}
    if ring: out["ring_nodes"]={str(k):det.ev[k] for k in range(1,9)}
    return out

def schedules(laps=20):
    return {
      "empty_single":[[0] for _ in range(laps)],
      "empty_two":[[0,16] for _ in range(laps)],
      "stop_after_5":[[0] if k<5 else [] for k in range(laps)],
      "omit_at_5":[[0] if k!=5 else [] for k in range(laps)],
      "extra_at_5":[[0,16] if k==5 else [0] for k in range(laps)],
      "add_second_at_5":[[0] if k<5 else [0,16] for k in range(laps)],
      "remove_second_at_8":[[0,16] if k<8 else [0] for k in range(laps)],
      "switch_0_to_16":[[0] if k<8 else [16] for k in range(laps)],
      "phase_1":[[1] for _ in range(laps)]
    }

def main():
    sc=schedules()
    return {
      "logic":{"XOR":truth([-4.5,-4.5]),"AND":truth([-2.5,-2.5]),
               "innovation":truth([-5,5]),"omission":truth([5,-5]),
               "lag_1":logic([1,1],[-4.5,-4.5],[0,1])[-1]},
      "parity":{"scan_start":-14,"scan_stop":-1,"step":0.25,
                "three_input_parity_candidates":[r["weight"] for r in parity_scan()
                if r["response_0_1_2_3_inputs"]==[0,1,0,1]]},
      "learn":{name:learn(s) for name,s in sc.items()},
      "controls":{"no_feedback":learn(sc["empty_single"],write=False,erase=False),
                  "write_only_stop":learn(sc["stop_after_5"],erase=False)}
    }

if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--output",default="-")
    args=a.parse_args()
    payload=json.dumps(main(),indent=2)
    if args.output=="-": print(payload)
    else:
        Path(args.output).parent.mkdir(parents=True,exist_ok=True)
        Path(args.output).write_text(payload+"\n")
        print("Wrote",args.output)
