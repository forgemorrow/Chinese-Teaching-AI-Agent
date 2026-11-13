# 📚 Chinese-Teaching-AI-Agent

English | [简体中文](./README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![CI](https://github.com/forgemorrow/Chinese-Teaching-AI-Agent/actions/workflows/ci.yml/badge.svg)](https://github.com/forgemorrow/Chinese-Teaching-AI-Agent/actions/workflows/ci.yml)

An LLM-powered lesson-preparation assistant tailored for K-12 Chinese language teachers, built with **Streamlit** and **Anthropic-compatible streaming APIs (MiMo)**.

## Overview

- **Full Curriculum Index**: Covers 3 grade levels and 24 textbook volumes (Elementary Grades 1–6, Middle School Grades 7–9, High School Grades 10–12) in `语文AI教学智能体/data/textbooks.py`.
- **Five Structured Workflows**: Deep text analysis, full lesson-plan generation, classroom interaction simulation, tiered homework design, and reading/writing guidance.
- **One-Click Export**: Streams structured Markdown responses and exports formatted `.md` and `.docx` documents (`python-docx`).

## QuickStart

```bash
git clone https://github.com/forgemorrow/Chinese-Teaching-AI-Agent.git
cd Chinese-Teaching-AI-Agent/语文AI教学智能体
pip install -r requirements.txt
export MIMO_API_KEY="your-api-key"
streamlit run app.py
```

Open `http://localhost:8501` in your browser (or configure the API key directly in the sidebar).

## Verification

```bash
pip install pytest python-docx
pytest tests/ -v
```

## License

Released under the [MIT License](LICENSE).
