#028feedback and020progress audit

The quoted correction correctly distinguishes continued scanning from successful endpoint updates. The actual full run reads3027FX and returns24 committed strokes plus cacheFX148→149. This is consistent with the current reject/continue/EOF actions and does not itself violate any geometric condition.

A focused independent numeric reviewer ran one read-only actual input pipeline and one Bi.scan (no broad suite or artifact-generating scripts). It reproduced the stored full result. FX150 is a higher top2824 than cached A2818 but fails reversal spacing1; FX151 is a lower bottom2794 than cached B2802, yet extension fails because it includes the higher top. All2877later decisions have zero successful updates. See numeric-review.md for exact intervals, centers and counts.

An independent reasoning review proves that the higher top permanently violates future bottom extensions' fixedA upper bound, while the lower bottom permanently violates future top reversals' fixedB lower bound. With unchanged history and the same selection rules, the cache/R can never update even though reads continue. This is a substantive limitation IF sustained later stroke production is intended; it is not evidence that an ordinary openEOF alone is invalid or that existing strokes violate the six conditions. No new reset/reselection/rollback policy was adopted.

This task changed no memo, production code or source data. inspected-hashes.json confirms the inspected020/028/bi.py remained unchanged. Records distinguish this focused reproduction/proof from the prior full-data tests and from the separate Q-return consistency work.
