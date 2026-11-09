# Chan Axiom Syntax

## 000 — Scope

- Provide a reusable template for understanding and implementing concepts in Chan theory.
- Develop the content through collaboration between the human author and AI.
- Use this template to document each concept’s definition, algorithm and underlying reasoning.

## 001 — Definition (What)

Use these three criteria selected from Kelley and Hutchins’ rules for definitions.[1]

- **Essential attributes:** State the fundamental characteristics that make the feature what it is and distinguish it from related concepts.
- **Correct scope:** Include every valid instance of the feature and exclude every invalid instance, making the definition neither too broad nor too narrow.
- **Clarity:** Use precise, understandable terms and explicit conditions; avoid vague, obscure or metaphorical wording.

## 002 — Algorithm (How)

Use these three checks, adapted from Erickson’s guidance on problem specification, algorithm description, correctness proofs and running-time analysis.[2]

- **Precision:** Specify the inputs, outputs and executable steps, including branches, repeated operations and stopping conditions.
- **Correctness:** Explain why the procedure produces results satisfying the definition for every permitted input. Worked examples support this explanation but do not establish correctness for all cases.
- **Efficiency:** Explain how the computational cost grows with input size, especially the running time.

### 002.a — Algorithm Tree

Show the algorithm’s branches, the condition for each branch and the resulting action.

### 002.b — Detailed Implementation Example

Walk through the algorithm step by step with a concrete example, explaining details that would otherwise remain abstract.

### 002.c — Helper Functions

Describe reusable functions called by the algorithm, including each function’s purpose, inputs and outputs.

### 002.d — Pseudocode

Express the algorithm in pseudocode, following the tree, worked example and helper functions in 002.a–002.c.

## 003 — Reasoning (Why)

Explain the trading rationale behind the concept and algorithm, drawing on relevant academic papers and other ideas.

## 004 — Other Notes

Record additional observations and implementation notes.

## 005 — Gaps and Pending Items

List unresolved questions, missing evidence and decisions or work still pending.

## Appendix A — Quotes from ChanOriginal

Collect relevant original passages with lesson or section references, and link each passage to the definition or algorithm rule it supports.

## Appendix B — Notes from CC's implementation

Collect relevant original passages with lesson or section references, and link each passage to the definition or algorithm rule it supports.
## References

[1] Kelley D, Hutchins D. *The Art of Reasoning: An Introduction to Logic*. 5th ed. Section 1.5, [“Rules for Definitions”](https://nerd.wwnorton.com/ebooks/epub/artofreasoning5/EPUB/content/1.1.5-chapter01.xhtml).

[2] Erickson J. *Algorithms*. 1st ed. 2019. Sections 0.5–0.6, [“Describing Algorithms” and “Analyzing Algorithms”](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf#page=11).
