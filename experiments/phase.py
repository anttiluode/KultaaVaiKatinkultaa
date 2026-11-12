"""Two native offset coincidence receivers: can spike pattern sign early/late error?"""
import sys,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from gn27 import Net,Beats,settle,RELAY

def phase_case(world_offset,pred_offset=2):
    # Source 0 (world) and source 1 (prediction), two XOR-like receivers.
    # Receiver 2 delays world by 1; receiver 3 delays prediction by 1.
    edges=[(0,2,-4.5,1),(1,2,-4.5,0),
           (0,3,-4.5,0),(1,3,-4.5,1)]
    net=settle(Net([RELAY]*4,edges))
    det=Beats(4)
    for t in range(28):
        sp=np.zeros(4)
        if world_offset<=t<world_offset+2: sp[0]=-10
        if pred_offset<=t<pred_offset+2: sp[1]=-10
        det.see(net.step(sp_ext=sp),t)
    return {"world":det.ev[0],"prediction":det.ev[1],
            "world_delayed":det.ev[2],"prediction_delayed":det.ev[3]}

def main():
    return {str(delta):phase_case(2+delta,2) for delta in [-2,-1,0,1,2]}

if __name__=="__main__":
    print(json.dumps(main(),indent=2))
