# Tutor Vision

An intelligent exam paper generator and course recommendation system that analyzes your syllabus and matches it with relevant NPTEL courses while providing learning resources and generating practice question papers.

## Table of Contents

- [Features](#features)
- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Setup Guide](#quick-setup-guide)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Usage Guide](#usage-guide)
- [Project Architecture](#project-architecture)
- [Contributing](#contributing)
- [License](#license)

## Features

✨ **Core Features:**
- 📄 **PDF Syllabus Upload** - Upload course syllabuses in PDF format
- 🤖 **Course Matching** - Intelligent matching with NPTEL courses using embeddings and similarity scoring
- 📚 **Learning Resources** - Automatic extraction of keywords and relevant learning resources from Google
- 📝 **Question Paper Generation** - Generate practice question papers based on syllabus content
- 🎯 **Course Recommendations** - Get top 8 most relevant courses with similarity scores
- 📊 **NLP Processing** - Advanced text preprocessing and keyword extraction

## Project Overview

Tutor Vision is designed to help educators and students:
1. **Analyze Syllabuses** - Extract and process course content from PDF documents
2. **Find Relevant Courses** - Discover similar NPTEL courses using AI-powered matching
3. **Resource Discovery** - Automatically find supplementary learning materials
4. **Assessment Creation** - Generate practice question papers for exams

## Tech Stack

**Backend:**
- FastAPI - Fast web framework for APIs
- Python 3.x
- NLTK - Natural Language Toolkit for text processing
- spaCy - Industrial-strength NLP library
- PyMuPDF - PDF text extraction
- scikit-learn - Machine learning and similarity computation

**Frontend:**
- React 18.3 - UI library
- Vite - Fast build tool and dev server
- Tailwind CSS - Utility-first CSS framework
- Axios - HTTP client
- Framer Motion - Animation library
- React Dropzone - File upload component

**Data:**
- NPTEL course dataset (JSON format)
- Course metadata (CSV format)
- Similarity scores caching

## Project Structure

```
Exam-Paper-Generator/
├── backend/                          # FastAPI backend
│   ├── src/
│   │   ├── app.py                   # Main FastAPI application
│   │   ├── data_preprocessing/      # Text preprocessing utilities
│   │   ├── generating_embeddings/   # Embedding generation for courses & users
│   │   ├── similarity/              # Similarity matching algorithms
│   │   ├── user_syllabus_processing/ # PDF extraction & processing
│   │   ├── getResources/            # Resource search & ranking
│   │   └── utils/                   # Utility functions
│   ├── data/                         # Dataset files
│   │   ├── raw/                     # Original NPTEL course data
│   │   └── processed/               # Processed datasets
│   ├── data_scrape/                 # Web scraping scripts
│   ├── artifacts/                   # Generated outputs
│   ├── logs/                        # Application logs
│   └── requirements.txt             # Python dependencies
│
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── components/              # React components
│   │   ├── services/                # API service layer
│   │   ├── types/                   # TypeScript type definitions
│   │   └── App.tsx                  # Main App component
│   ├── public/                      # Static assets
│   ├── package.json                 # NPM dependencies
│   └── vite.config.js               # Vite configuration
│
└── README.md                         # This file
```

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **pip** - Python package manager (comes with Python)
- **npm** - Node package manager (comes with Node.js)

## Quick Setup Guide

### The "One-Click" Setup (For Team Members on Windows)

1. **Run the Setup Script**
   Double-click `setup_windows.bat` in the root folder.
   This script will automatically:
   - Create a Python virtual environment
   - Install all backend requirements
   - Download necessary NLP models
   - Copy `.env.example` to `backend/.env`
   - Install all React frontend dependencies

2. **Add API Keys**
   Open `backend/.env` and add your free API keys for the LLMs.
   (Links to get them are included inside the `.env` file).

3. **Resources Folder**
   Place your standard syllabuses in `resources/syllabuses/` and Past Year Question (PYQ) papers in `resources/pyqs/`. This keeps them handy whenever you want to upload and run the code.

4. **Start the App**
   Double-click `start_tutorvision.bat` to launch both backend and frontend servers automatically!

### Manual Setup (For Reference/Other OS)

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Verify installation:**
   ```bash
   npm list
   ```

## Configuration

# Backend Configuration
UPLOAD_DIR=artifacts/question_papers
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173


### Backend Configuration Files

- `backend/artifacts/` - Upload and output directory
- `backend/logs/` - Application logs
- `backend/data/processed/` - Processed course datasets

### Frontend Configuration

Update API endpoint in `frontend/src/services/api.tsx` if running on a different host:

```typescript
const API_BASE_URL = 'http://localhost:8000'; 
```

## Running the Application

### Start the Backend Server

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Activate virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Start FastAPI server:
   ```bash
   python -m uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Start the Frontend Server

1. In a new terminal, navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

   The application will be available at: `http://localhost:5173`

## API Endpoints

### Upload Syllabus

**POST** `/upload`

Upload a PDF syllabus file.

**Request:**
```
Content-Type: multipart/form-data
Body: { file: <PDF File> }
```

**Response:**
```json
{
  "message": "File 'syllabus.pdf' uploaded successfully.",
  "file_path": "artifacts/syllabus.pdf"
}
```

### Get Course Recommendations

**POST** `/get_courses`

Get top 8 NPTEL courses matched with the uploaded syllabus.

**Response:**
```json
[
  {
    "id": "course_001",
    "title": "Course Name",
    "instructors": ["Prof. Name"],
    "duration": "12 weeks",
    "url": "https://nptel.ac.in/course/...",
    "similarity": 0.87
  }
]
```

### Get Learning Resources

**POST** `/get_resources`

Extract keywords and get relevant learning resources.

**Response:**
```json
{
  "keywords": ["keyword1", "keyword2", ...],
  "resources": [
    {
      "title": "Resource Title",
      "url": "https://example.com",
      "relevance_score": 0.95
    }
  ]
}
```

### Generate Question Paper

**POST** `/generate_paper`

Generate a practice question paper based on the syllabus.

**Response:**
```json
{
  "questions": [...],
  "paper_id": "paper_123",
  "file_path": "artifacts/question_papers/paper_123.pdf"
}
```

## Usage Guide

1. **Open the Application**
   - Visit `http://localhost:5173` in your browser

2. **Upload Syllabus**
   - Click the upload area or drag-and-drop a PDF file
   - Wait for the file to be processed

3. **View Recommended Courses**
   - See the top 8 matching NPTEL courses with similarity scores
   - Click course links to visit NPTEL

4. **Explore Learning Resources**
   - View extracted keywords from your syllabus
   - Access recommended learning materials
   - Sort by relevance

5. **Generate Question Papers**
   - Generate practice exams based on syllabus content
   - Download generated papers in PDF format

## Project Architecture

### Data Flow

```
PDF Upload
    ↓
PDF Text Extraction
    ↓
Text Preprocessing & Cleaning
    ↓
Keyword & Embedding Generation
    ↓
Similarity Matching with NPTEL Courses
    ↓
Ranking & Filtering (Top 8 Courses)
    ↓
Display Results & Resources
```

### Key Components

**Backend:**
- `extract_from_pdf.py` - Extracts text from PDFs
- `preprocessing.py` - Text cleaning and normalization
- `course_embedding.py` - Generates embeddings for courses
- `user_embedding.py` - Generates embeddings for user syllabuses
- `matching.py` - Computes similarity scores
- `ranking.py` - Ranks courses by relevance
- `search.py` - Searches for learning resources
- `generate_paper.py` - Creates question papers

**Frontend:**
- `FileUpload.tsx` - Handles PDF uploads
- `Results.tsx` - Displays matching courses
- `Resources.tsx` - Shows learning resources
- `SetQuestionPaper.tsx` - Question paper generation interface

## Contributing

Contributions are welcome! Please feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests


**For questions or support, please open an issue on the repository.**
