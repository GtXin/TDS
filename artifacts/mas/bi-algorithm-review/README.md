# Read-only review: return to020002.a

The current implementation matches the current decision tree's fixed-earliest-A, first-qualified-reverse and mandatory-extension behavior. This review changes neither. It tests whether the resulting behavior meets the continuous-drawing goal.

Run the three targeted reproductions:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python artifacts/mas/bi-algorithm-review/reproduce.py
```

`diagnosis.json` records actual current-chain outputs, independently calculated six-rule edges for seed50 and the compact9bar case, and verification of the existing full-sample definition-valid witness. Protected memo/code/test hashes are unchanged.

The compact case has merged intervals `[x,x+1]`, lows `8,9,6,4,2,0,11,-1,0`. Exact extrema are top1,bottom5,top6,bottom7. The sole legal pair is1→5. Top6 cannot be a reverse because its center is only1position after bottom5; lowerbottom7 cannot extend fromtop1 because the interior top6 has high12 above top1's high10. There is no legal connected continuation from that fixedA. Caching cannot change that fact.

On the10060raw sample, current code returns0routes after3177states, blocking atFX151. The pre-existing independent geometric witness has480valid strokes from the sameinitialFX0 through lastFX3026; all pairs were rechecked. Near the failure, current choice145→148 differs from witness145→150. The witness does not obey all current temporal selection rules and is not adopted as a canonical result; it establishes that geometric feasibility and policy reachability are different questions.

Recommendation: revisit0202.6–2.8, keep028 and its tests as a reproducible baseline, and explicitly separate output legality, implementation/reference conformance and intended coverage. Preserve the confirmed fixedA while diagnosing. Decide what happens to a valid historical prefix when later continuation is impossible, and separately investigate reverse-choice checkpoints where a geometric continuation exists. Edit020 before any policy/code synchronization.
