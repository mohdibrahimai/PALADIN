"""Training scripts for PALADIN.

These scripts illustrate how one might fine‑tune a model to emit
evidence graphs from human labelled data.  In this repository we do
not perform any heavy training by default.  Instead, the scripts
read the JSONL files containing minimal graphs and print summary
statistics.  You can adapt them to your own training pipeline or
integrate external libraries such as transformers and PEFT when you
have access to GPUs and network connectivity.
"""