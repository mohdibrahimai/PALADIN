# Proof-Answers

Proof-Answers (formerly PALADIN) is a research prototype and reference implementation of a verifiability‑first answering engine. The goal of Proof-Answers is to train models that produce **answers together with a machine‑checkable proof** in the form of a minimal evidence graph. A deterministic verifier checks that the evidence graph supports the answer, validates hashes of cited sources, and re‑executes numeric or date operations for correctness. Human annotators supply the first batch of minimal graphs, which supervise the proof planner; reinforcement learning can then reward the planner for producing valid proofs.

This repository contains a complete end‑to‑end skeleton of the Proof-Answers system: a schema and compiler for evidence graphs, a simple retriever, a rule‑based answerer and proof planner, a verifier with hash and minimality checks, and a thin user interface. It is meant to demonstrate the overall architecture and serve as a starting point for experimentation rather than a production‑ready service handling large‑scale traffic. All components are written in pure Python and avoid heavy dependencies so they can run in restricted environments.

## Quick Start

1. **Install dependencies.**  The core Proof-Answers code relies on the standard library and a few common packages (`numpy`, `pandas`, `matplotlib`). To run the Streamlit user interface you will also need `streamlit` and `reportlab` for PDF export:

   ```bash
   pip install streamlit reportlab
   ```

2. **Prepare a document collection.**  The retriever needs a set of documents to search over. For demonstration, place a file `docs.json` in the `data` directory with entries like:

   ```json
   { "id": "doc1", "text": "your text here" }
   ```

   In real use, index trusted sources such as encyclopedias or news.

3. **Run the user interface.**  From the repository root:

   ```bash
   streamlit run proof_answers/app/ui.py
   ```

   Enter a natural language question. The app retrieves candidate documents, generates an answer and a minimal evidence graph, verifies the proof, and shows a pass/fail indicator. You can also export proof‑carrying answer cards as PDFs.

4. **Label human graphs (optional).** Use the labeler in `proof_answers/labeler/ui.py` to create minimal evidence graphs for a seed set of questions. The resulting JSONL file in `data/human_graphs` can then be used to fine‑tune the proof planner.

5. **Train a planner (advanced).**  Training scripts in `proof_answers/training` illustrate how to fine‑tune a small model using human graphs. These scripts are illustrative only—by default they don’t launch real GPU training. See `training/sft_graphs.py` for guidance on adapting them to your infrastructure.

## Repository Layout

```
proof_answers/
  README.md              # this file
  app/                   # user interfaces (CLI and Streamlit)
  ci/                    # CI config and quality gates
  data/                  # document collection and human graphs
  egl/                   # evidence graph language definitions and compiler
  evals/                 # evaluation metrics
  model/                 # simple answerer and proof planner
  retriever/             # document retrieval and span extraction
  scripts/               # helper scripts for sets, evals
  tests/                 # unit tests covering core functionality
  training/              # fine tuning and RL scripts (illustrative)
  verifier/              # deterministic proof checker
```

## Limitations & Future Work

This repository provides a minimalist, self‑contained implementation. It does not perform heavy machine learning by default, instead using heuristics for answer generation, retrieval, and inference. For a production‑grade system:

* Integrate robust retrieval components.
* Train the planner on a large, human‑labelled corpus.
* Replace the heuristic verifier with stronger entailment models.

The provided training scripts act as a scaffold for these future extensions.
