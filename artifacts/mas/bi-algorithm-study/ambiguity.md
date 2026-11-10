# Stroke endpoint-subset ambiguity study

## Model and scope
Input is a finite chronological series of nonzero integer price intervals [low,high],
with no inclusion between adjacent bars (equal-boundary enclosure also counts).
Every strict three-bar top/bottom is a candidate, including overlapping windows.
A valid directed edge joins opposite candidates with center gap>=4, endpoint
global extrema over their inclusive center-to-center interval, and both strict
center-bar inequalities. A path shares endpoints and alternates direction.
All compared paths have identical first/last candidate centers and cover the
whole center interval, so this is not merely different prefixes or tail handling.
All inputs are synthetic processed bars; this is a mathematical experiment, not
a production stroke implementation, a source-selection algorithm, or a CC run.

## Formalization
For chronological candidate centers i<j, require opposite kinds and j-i>=4.
Let T,B be their top/bottom centers. For every i<=k<=j, require
high[k]<=high[T] and low[k]>=low[B]. Also require high[T]>high[B]
and low[B]<low[T]. Paths are increasing center subsequences with every consecutive
pair passing that edge predicate. Opposite endpoints plus shared endpoints imply
alternating directions. The two strict interval inequalities follow from strict
fractals and endpoint global extrema; they are checked explicitly nevertheless.

## Counterexample without endpoint ties
Use low values (bar high=low+1):
8,9,8,7,5,3,4,5,6,7,4,2,3,4,5,6,5,3,1,0,1.
The exact candidate list is top1,bottom5,top9,bottom11,top15,bottom19.
Two valid full paths are (1,5,9,19) and (1,11,15,19); each has three strokes.
Same-type endpoint extreme prices are distinct. Span19-1=18 and gap>=4 imply
at most four strokes; top-to-bottom alternation requires an odd count, so the
maximum is three, attained by BOTH paths. They are also nonrefinable: inserting
all internal reversals would require the invalid gap9->11=2. Thus maximizing
stroke count or forbidding further endpoint insertion does not ensure uniqueness.
The direct coarse path (1,19) is a third valid path under the bare six rules.

## Additional cases
A 15-bar case has paths (1,13) and (1,5,9,13), showing coarse-vs-refined ambiguity.
A 17-bar case has equal-price bottom candidates at5,7, with distinct maximum-count
paths choosing one or the other. Ties matter, but the 21-bar witness proves that
tie-breaking alone is insufficient. All bar arrays, exact candidates, legal edges,
and enumerated full/maximal/maximum-count paths are in ambiguity.json.

## Search and checks
The script enumerates every fixed-boundary path in each candidate DAG, then checks
every returned path using an independent direct checker. Strict-fractal tests
are also cross-checked against joint-direction changes. It separately enumerates
all 24 assignments of four distinct interior extrema1..4 between fixed outer
extrema5,0 at centers1,5,9,11,15,19, retaining only strict zigzags. This bounded
family search is NOT exhaustive over all continuous bar sequences. JSON records
actual family and ambiguity counts, Python version and source snapshot hashes.
Reproduce: python3 artifacts/mas/bi-algorithm-study/ambiguity.py

## Consequences and limits
The six structural rules are necessary compatibility checks, not a unique subset
selection policy. A source-derived earliest-pair/extension/replacement rule may
choose among these paths or reject them for additional reasons; it must be stated
and analyzed separately. These experiments do not refute a fuller original-source
definition that imposes such additional selection rules. Boundary start/end,
equal extrema, provisional tails and behavior after revisions remain separate
specification choices. Full coverage here means the fixed center interval, not the
unconfirmed flanking bars outside its endpoint centers. Requiring every candidate
to be selected generally conflicts with gap>=4 and is not implied by the memo.

## Complexity
Let n be bars, m<=n-2 candidates, e legal edges. Strict-fractal scan is O(n).
This deliberately simple checker builds its DAG by O(m^2) interval scans, using
O(n*m^2) time and O(m+e) graph storage. Enumerating paths can be exponential in m;
independent validation is O(n) per returned full path. A proposed algorithm can
preprocess range minima/maxima in O(n log n) storage/time, check pairs in O(1),
and build the graph in O(m^2) time. DAG reachability/count capped at2 or a maximum-
count path can then be found in O(m+e), but the objective/tie policy is a NEW design
decision, not a consequence of the six rules. These bounds use the word-RAM model
for bounded integer input; this finite script is not a scalability benchmark.

