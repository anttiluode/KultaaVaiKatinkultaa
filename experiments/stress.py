"""Stress fixed-period native memory. Separate source pulse encoding from memory."""
import json
import random
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"experiments"))
from kultaa import learn

def evaluate(phases,laps=12):
    r=learn([phases for _ in range(laps)])
    start,end=2*32,laps*32
    # A 2-tick pulse entering a native source normally yields a beat 4 ticks later.
    requested={lap*32+p+4 for lap in range(2,laps)
               for p in phases if start<=lap*32+p+4<end}
    world={t for t in r["world"] if start<=t<end}
    predicted={t for t in r["prediction"] if start<=t<end}
    # Evaluate memory against actual world events; report source encoding separately.
    return {
      "phases":phases,
      "requested_events":len(requested),
      "world_events":len(world),
      "source_missed":len(requested-world),
      "source_extra":len(world-requested),
      "prediction_correct":len(predicted&world),
      "prediction_missed":len(world-predicted),
      "prediction_extra":len(predicted-world),
      "post_lap2_errors":sum(start<=t<end for t in r["innovation"]+r["omission"]),
    }

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
            rng=random.Random(seed)
            schedule=[[(16+rng.randint(-spread,spread))%32]
                      for _ in range(20)]
            ev=learn(schedule)
            jitter.append({"spread":spread,"seed":seed,
                           "innovation":len(ev["innovation"]),
                           "omission":len(ev["omission"]),
                           "last_prediction":ev["prediction"][-1] if ev["prediction"] else None})
    end_to_end=sum(1 for d in records if
                   not (d["source_missed"] or d["source_extra"] or
                        d["prediction_missed"] or d["prediction_extra"]))
    memory_exact=sum(1 for d in records if
                     not (d["prediction_missed"] or d["prediction_extra"]))
    source_exact=sum(1 for d in records if
                     not (d["source_missed"] or d["source_extra"]))
    return {"protocol":"32-tick native relay ring, 2-tick source pulses, 12 laps, score last 10",
            "patterns":records,"pattern_count":len(records),
            "end_to_end_exact":end_to_end,
            "source_encoding_exact":source_exact,
            "memory_prediction_exact":memory_exact,
            "jitter":jitter}

if __name__=="__main__":
    result=run()
    if len(sys.argv)>1:
        Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+"\n")
    print("END TO END EXACT",result["end_to_end_exact"],"/",result["pattern_count"])
    print("SOURCE ENCODING EXACT",result["source_encoding_exact"],"/",result["pattern_count"])
    print("MEMORY PREDICTION EXACT",result["memory_prediction_exact"],"/",result["pattern_count"])
    for p in result["patterns"]:
        if p["source_missed"] or p["source_extra"] or p["prediction_missed"] or p["prediction_extra"]:
            print("IMPERFECT",p)
    for j in result["jitter"]:
        print("JITTER",j)
