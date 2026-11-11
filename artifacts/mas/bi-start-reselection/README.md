# A becomes C: framework discussion, not a rule change

The user proposes reselecting A as later top C and questions whether two cache levels suffice. One read-only upstream numeric run (no Bi.scan) verifies the actual replacement chain P=FX145→C=FX150→D=FX151. P→C has center gap13,min2778,max2824; C→D gap4,min2794,max2824. Both pairs and their shared endpoint/direction satisfy the six conditions. See pair-review.md.

The current run already submitted P→A as R's last stroke before seeing C/D. Resetting only the working start to C would disconnect it from R's endA; replacing P→A by P→C would modify finalR. Therefore a future proposal must retain that predecessor in an unsubmitted region and revise the commit timing, rather than silently edit currentR.

CurrentBi001 usually holds only a start; Bi002 holds one complete cached stroke. That differs from retaining two complete unsubmitted strokes. Two full pending strokes plus each arriving candidate would permit this local rewrite while preserving an earlier finalR, but neither sufficiency nor a minimum number of levels has been proved. If a replacement pair fails its full range check, still earlier endpoints may be affected; a justified immutable commit boundary remains the key design obligation. See framework-review.md.

This discussion adopts no new transition, fixed cache depth or recovery rule. Memos, code and datasets were not changed. Root records only the proposed direction and verified local feasibility.
