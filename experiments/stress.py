"""Stress diagnostics for fixed-period native memory; report results, do not alter core."""
import json
import random
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"experiments"))
from kultaa import learn

def evaluate(phases,laps=12):
    events=learn([phases for _ in range(laps)])
    # For a 2-tick native world pulse at phase p, source beat is at phase p+4.
    target={lap*32+p+4 for lap in range(2,laps) for p in phases}
    observed={t for t in events["prediction"] if t>=64}
    ok=target&observed
    return {"phases":phases,"expected":len(target),"correct":len(ok),
            "missed":len(target-observed),"extra":len(observed-target),
            "post_lap2_errors":sum(t>=64 for t in events["innovation"]+events["omission"])}

def run():
    rng=random.Random(27)
    patterns=[[0],[0,16],[0,8,16,24],[0,2],[0,4],[0,4,8],
              [0,4,8,12,16,20,24,28],[0,2,4,6],[3,11,19,27]]
    for n in range(1,7):
        for _ in range(4):
            patterns.append(sorted(rng.sample(list(range(0,32,2)),n)))
    records=[evaluate(p) for p in patterns]
    jitter=[]
    for spread in (0,1,2,3):
        for seed in range(4):
            r=random.Random(seed)
            schedule=[[(16+r.randint(-spread,spread))%32] for _ in range(20)]
            ev=learn(schedule)
            jitter.append({"spread":spread,"seed":seed,"innovation":len(ev["innovation"]),
                           "omission":len(ev["omission"]),
                           "last_prediction":ev["prediction"][-1] if ev["prediction"] else None})
    return {
       "protocol":"Same native net, no weight learning, 32-tick ring, 2-tick world event",
       "patterns":records,
       "pattern_exact":sum(int(v["missed"]==0 and v["extra"]==0) for v in records),
       "pattern_count":len(records),
       "jitter":jitter
    }

if __name__=="__main__":
    d=run()
    if len(sys.argv)>1:
        Path(sys.argv[1]).write_text(json.dumps(d,indent=2)+"\n")
    print("PATTERNS EXACT",d["pattern_exact"],"of",d["pattern_count"])
    for rec in d["patterns"]:
        if rec["missed"] or rec["extra"]:
            print("FAIL",rec)
    for rec in d["jitter"]:
        print("JITTER",rec)
