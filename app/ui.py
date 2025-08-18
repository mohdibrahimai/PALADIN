"""Interactive user interface for PALADIN.

This Streamlit application allows users to submit natural language
questions to PALADIN, view the answer together with its evidence
graph, and see whether the proof passed verification.  Users can
optionally export a proof carrying answer card as a PDF via the
``report.py`` module.
"""

from __future__ import annotations

import json
import os
from typing import Optional

import streamlit as st

from ..retriever.retrieve import SimpleRetriever
from ..model.runner import PaladinRunner
from ..app.report import generate_report


def load_retriever() -> SimpleRetriever:
    docs_path = os.path.join(os.path.dirname(__file__), "..", "data", "docs.json")
    docs_path = os.path.normpath(docs_path)
    retriever = SimpleRetriever.from_json(docs_path)
    return retriever


def main() -> None:
    st.set_page_config(page_title="PALADIN", layout="wide")
    st.title("PALADIN – Proof‑Carrying Answer Engine")
    st.write("Enter a question below. PALADIN will attempt to answer it and show a minimal evidence graph.")
    retriever = load_retriever()
    runner = PaladinRunner(retriever)
    query = st.text_input("Question")
    if st.button("Run", disabled=not query):
        with st.spinner("Retrieving and verifying..."):
            result = runner.answer_and_proof(query)
        st.subheader("Answer")
        st.write(result["answer"])
        st.subheader("Proof Validity")
        if result["valid"]:
            st.success("PASS: Proof is valid")
        else:
            st.error("FAIL: Proof is invalid")
        st.subheader("Evidence Graph (JSON)")
        st.json(result["graph"])
        st.subheader("Verification Details")
        st.json(result["details"])
        if st.button("Export Answer Card"):
            # Write report to a temporary file in /tmp
            out_path = "/tmp/paladin_report.pdf"
            generate_report(out_path, query, result)
            with open(out_path, "rb") as f:
                st.download_button(label="Download Answer Card", data=f, file_name="answer_card.pdf")


if __name__ == "__main__":
    main()