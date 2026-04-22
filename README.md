# TutorVision: AI-Powered Intelligent Exam Paper Generator

> **Abstract** : TutorVision is an AI-powered intelligent exam paper generator designed to assist educators in creating customized, balanced, and syllabus-aligned examination papers with minimal effort. Leveraging Natural Language Processing (NLP) and machine learning techniques, the system analyzes course material, question banks, and difficulty levels to generate diverse question sets—ranging from MCQs to descriptive questions—tailored to specific learning outcomes. TutorVision ensures coverage of Bloom’s Taxonomy, maintains topic weightage, and avoids redundancy through smart filtering. With an intuitive interface and automated formatting, it significantly reduces manual workload while enhancing the quality and fairness of assessments in educational institutions.

### Project Members
1. JETHAM AYAAN RIYAZ  [ Team Leader ] 
2. SAYYED MOHAMMED ZAID GULSHER ALAM 
3. NOMANI TAHA RAHIL 
4. KHAN RAMSHA AYUB AHMED 

### Project Guides
1. PROF. ANUPAM CHOUDHARY  [ Primary Guide ] 

### Deployment Steps
Please follow the below steps to run this project.
1. **Run the Install Script**: Double-click `setup_windows.bat` in the root folder to install backend and frontend dependencies.
2. **Configure Environment**: Open the generated `backend/.env` file and enter your required API Keys.
3. **Load Resources**: Place your syllabus PDFs in `resources/syllabuses/` and Past Year Question papers in `resources/pyqs/`.
4. **Start Application**: Double-click `start_tutorvision.bat` to launch both the backend server and frontend UI.

### Subject Details
- Class : BE (COMP) Div A - 2025-2026
- Subject : Major Project 1 (MajPrj-1)
- Project Type : Major Project

### Platform, Libraries and Frameworks used
1. [Python 3.10+](https://www.python.org)
2. [FastAPI](https://fastapi.tiangolo.com)
3. [ReactJS 18](https://reactjs.org)
4. [Vite](https://vitejs.dev/)
5. [TailwindCSS](https://tailwindcss.com/)
6. [PyMuPDF](https://pymupdf.readthedocs.io/)

### Dataset Used
1. Custom University Syllabus & Past Year Question Paper (PYQ) PDFs

---

## Project Description

An intelligent, AI-powered exam paper generator and course recommendation system. TutorVision analyzes academic syllabuses along with past year questions (PYQs) to automatically curate university-level exam papers, MCQ quizzes, study question banks, and map relevant NPTEL courses.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Overview & Architecture](#project-overview--architecture)
- [Prerequisites](#prerequisites)
- [Quick Setup (For PC / Team Members)](#quick-setup-for-pc--team-members)
- [Using the Generator](#using-the-generator)
- [Troubleshooting & API Failover](#troubleshooting--api-failover)

---

## Features

✨ **Core Capabilities:**
- 📄 **Smart Exam Paper Generation:** Upload a Syllabus PDF and past exam papers, pick your repetition threshold, and instantly generate a formatted 80-mark university question paper (accessible in PDF & DOCX).
- 🧩 **MCQ Generator:** Quickly derive exactly 40 highly-relevant Multiple Choice Questions referencing specific past patterns.
- 📚 **Syllabus & Question Bank Tracking:** Automatically curates a targeted question bank organized by modules for extensive exam prep.
- 📉 **Course & Trend Analysis:** Visually analyze the syllabus-to-PYQ correlation to discover which modules represent the highest weightage for study efficiency.
- 🤖 **Resilient Multi-LLM Processing:** Built-in failover logic iterates over multiple top-tier providers (Groq, Together AI, Cerebras, Hugging Face, Gemini) to avoid rate limits and minimize setup costs. 

---

## Tech Stack

**Backend:**
- **FastAPI** - High-performance web framework for APIs routing.
- **Python 3.10+** - Core data processing.
- **PyMuPDF & PyPDF2** - High-fidelity text extraction.
- **FPDF & Python-Docx** - Exporting final document renders securely.

**Frontend:**
- **React.js 18** - Responsive user interface.
- **Vite** - Lightning-fast build tool and dev server.
- **Tailwind CSS** - Clean, modern, responsive aesthetics.
- **Framer Motion** - Smooth UI component transitions.

---

## Project Overview & Architecture

**How it works seamlessly:** 
1. **User Provides Data:** You place generic standard resources into `resources/pyqs/` and `resources/syllabuses/` so they remain continuously available to use.
2. **Text Extractions:** When uploaded inside the web-app, PyMuPDF extracts rich text efficiently.
3. **Prompt Construction:** The extracted data is formatted precisely according to current rules to dictate part sub-structures, instruction types, and answer key inclusion. 
4. **Resilient AI Execution:** The `generate_paper.py` backend class iteratively connects to active AI models until it finds a reliable connection to compute your paper. 
5. **Formatted Output:** Results manifest instantly on the UI — where an explicit Python endpoint generates secure Document downloads.

```text
Exam-Paper-Generator/
├── backend/                  # FastAPI backend
│   ├── artifacts/            # Output processing area (Logs, thresholds limit cache)
│   ├── src/                  
│   │   ├── app.py            # Primary endpoints defined here
│   │   └── utils/            # Essential generators (PDF layout, docx formatting, logic)
│   └── .env.example          # Template API configurations!
├── frontend/                 # React UI Client
│   ├── src/components/       # Isolated React generators (SetQuestionPaper, MCQPaper, etc)
│   └── package.json          # Dependency definitions
├── resources/                # Storage base for static papers (Not committed securely)
│   ├── pyqs/                 
│   └── syllabuses/          
├── setup_windows.bat         # Single-click setup script 
└── start_tutorvision.bat     # Single-click launch script
```

---

## Prerequisites

Before continuing, you merely need:
- **Python 3.10+** (Added directly to system PATH)
- **Node.js 18+**

---

## Quick Setup (For PC / Team Members)

We've automated the entire virtual environment assembly and module configurations using Windows batch scripts!

### 1. Run the Install Script
Double-click `setup_windows.bat` in the root folder. 
This script will automatically do all of the heavy lifting:
- Provision a Python virtual environment (`backend/venv`).
- Install all backend requirements & necessary spaCy NLP models.
- Download all React frontend dependencies (`node_modules`).
- Seed a baseline configuration (`.env`).

### 2. Enter API Keys
Open up the new `backend/.env` file. You need AT LEAST ONE key to run backend data processing. Link references to free key panels are already inside that `.env` file waiting for you.

### 3. Load Up Useful Resources
Store common course documents in `resources/syllabuses/` and Past Year Question (PYQ) papers in `resources/pyqs/`. This keeps them handy whenever you want to upload test materials rapidly!

### 4. Start the Environment
Double-click `start_tutorvision.bat` to launch!
It will spawn **both** the FastAPI python server and the Vite React server simultaneously in separate windows. 
Access the user interface immediately at `http://localhost:5173`.

---

## Using the Generator

1. **Upload Syllabus & Papers:** Utilize the `Set Question Paper` tab to pick standard `.pdf` course files. 
2. **Tune Difficulty & Thresholds:** Target repetition boundaries so past papers are properly respected alongside newer AI-inferences!
3. **Wait for Backend Compilation:** You'll see the loading indicator spin. Behind the scenes, the model attempts generations, sanitizes malicious JSON formatting mismatches, and compiles answers.
4. **Download Material:** Retrieve your output smoothly in either precise PDF formats, or Word Documents (`.docx`) for extra localized editing!

---

## Troubleshooting & API Failover 

During extremely prominent usage (or large PDF contexts), free-tier AI APIs easily rate-limit operations. 
TutorVision was distinctly configured with a **Failover Loop mechanism**:

- **If an Engine Fails:** It instantly captures the rate-limit errors and swaps seamlessly to the next defined fallback engine (i.e. From Groq → HuggingFace → Together...).
- **Malformed Outputs:** Sometimes models forget how to write explicit JSON syntax. TutorVision deploys an aggressive 6-step fallback parser that automatically sanitizes, strips out malicious markdown quotes, patches dangling bracket structures, and perfectly restores fragmented responses. 

Enjoy creating your test papers effortlessly! 
