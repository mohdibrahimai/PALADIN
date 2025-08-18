PALADIN
=======

PALADIN (Proof‑Carrying Answers) is a research prototype and reference
implementation of a verifiability‑first answer engine.  The goal of
PALADIN is to train models that produce **answers together with a
machine‑checkable proof** in the form of a minimal evidence graph.  A
deterministic verifier checks that the evidence graph supports the
answer, that hashes match the cited sources and that numeric or date
operations are correctly re‑executed.  Human annotators supply the
first batch of minimal graphs which are used to supervise the proof
planner; reinforcement learning can then reward the planner for
producing valid proofs.

This repository contains a complete end‑to‑end skeleton of the
PALADIN system: a schema and compiler for evidence graphs, a simple
retriever, a rule‑based answerer and proof planner, a verifier with
hash and minimality checks, and a thin user interface.  It is meant to
demonstrate the overall architecture and be a starting point for
experimentation rather than a production‑ready service handling
large‑scale traffic.  All components are written in pure Python and
avoid external dependencies where possible so that they can run in
restricted environments.

## Quick start

1.  **Install dependencies**.  The core PALADIN code only depends on
    the standard library and a few well‑known packages which should
    already be installed in most Python environments (e.g. `numpy`,
    `pandas`, `matplotlib`).  If you wish to run the Streamlit user
    interface you will also need to install `streamlit` and
    `reportlab` for PDF export.  A simple way to install these
    dependencies is:

    ```bash
    pip install streamlit reportlab
    ```

2.  **Create or obtain a document collection**.  The retriever needs a
    set of documents to search over.  For demonstration purposes you
    can place a file `docs.json` in the `data` directory with a list
    of objects of the form `{ "id": "doc1", "text": "your text here" }`.
    Real deployments should index news articles, encyclopaedia
    articles or other trusted sources.

3.  **Run the user interface**.  Execute the following command from
    the root of this repository to start the Streamlit app:

    ```bash
    streamlit run paladin/app/ui.py
    ```

    Enter a natural language question into the input box.  The app
    retrieves candidate documents, generates an answer and a minimal
    evidence graph, verifies the proof and displays a pass/fail
    indicator.  You can also export a proof‑carrying answer card as a
    PDF from the interface.

4.  **Label human graphs** (optional).  Use the labeler in
    `paladin/labeler/ui.py` to create minimal evidence graphs for a
    seed set of questions.  The resulting JSONL file in
    `data/human_graphs` can then be used to fine‑tune the proof
    planner.

5.  **Train a planner** (advanced).  The training scripts in
    `paladin/training` illustrate how one might fine‑tune a small
    language model using the human graphs.  These scripts are
    illustrative only—due to the restricted execution environment they
    do not launch a real GPU training job by default.  See the
    comments in `training/sft_graphs.py` for guidance on adapting
    these scripts to your own infrastructure.

## Repository layout

```
paladin/
  README.md              # this file
  app/                   # user interfaces (CLI and Streamlit)
  ci/                    # continuous integration config and quality gates
  data/                  # document collection and human labelled graphs
  egl/                   # evidence graph language definitions and compiler
  evals/                 # evaluation metrics
  model/                 # simple answerer and proof planner
  retriever/             # document retrieval and span extraction
  scripts/               # helper scripts for building sets, running evals
  tests/                 # unit tests covering core functionality
  training/              # illustrative fine tuning and RL scripts
  verifier/              # deterministic proof checker
```

## Limitations and future work

This repository provides a minimalist, self‑contained implementation
intended to run in constrained environments.  It does not perform any
heavy machine learning by default, instead relying on heuristics for
answer generation, retrieval and natural language inference.  To
deploy a real system one should integrate more robust retrieval
components, train the planner on a large human labelled corpus and
replace the heuristic verifier with stronger entailment models.  The
provided training scripts act as a scaffold for such efforts.