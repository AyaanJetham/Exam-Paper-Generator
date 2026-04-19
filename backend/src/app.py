from fastapi import FastAPI, File, UploadFile, File, Form
from .user_syllabus_processing.extract_from_pdf import extract_module_content
from .user_syllabus_processing.syllabus_preprocessing import preprocess_text
from .generating_embeddings.user_embedding import user_syllabus_embedding
from .generating_embeddings.course_embedding import course_embedding
from .similarity.matching import computing_similarity
from .similarity.rating import rate_courses
from .similarity.get_course import get_course_info, load_csv
from fastapi.middleware.cors import CORSMiddleware

from .utils.logger import Logger
import os
from werkzeug.utils import secure_filename
import json
import shutil  # For better file handling
import uvicorn
from fastapi.responses import JSONResponse
import os
import shutil
from .utils.generate_paper import TutorVisionAPI

UPLOAD_DIR = "artifacts/question_papers"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
logger = Logger.get_logger()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify domains here
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)
# Directory to save uploaded PDFs
UPLOAD_FOLDER = "artifacts"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variable to store the uploaded file path
uploaded_file_path = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the syllabus-to-course matching API!"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Check if the file is a PDF
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "Only PDF files are allowed."})
    
    global uploaded_file_path  # Use the global variable to store the file path
    try:
        # Save the file
        uploaded_file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(uploaded_file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        return {"message": f"File '{file.filename}' uploaded successfully.", "file_path": uploaded_file_path}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
@app.post("/get_courses")
async def compute_similarity():
    if not uploaded_file_path:
        return JSONResponse(status_code=400, content={"error": "No file uploaded."})

    try:
        # Extract module content from the uploaded PDF
        module_content = extract_module_content(uploaded_file_path)
        logger.info(f"Extracted Content: {module_content}")
        # Preprocess the text and compute embeddings for the user's syllabus
        processed_content = preprocess_text(module_content)  # User PDF syllabus
        logger.info(f"After preprocessing: {processed_content}")

        user_embedding = user_syllabus_embedding(processed_content)
      
        # Load NPTEL course data (for IDs and reference)
        json_file_path = "data_scrape/cleaned_scraped.json"
        with open(json_file_path, 'r') as file:
            nptel_data = json.load(file)

        # OPTIMIZATION: Load pre-computed embeddings if available
        cache_path = "artifacts/nptel_course_embeddings.json"
        if os.path.exists(cache_path):
            logger.info("⚡ Loading pre-computed NPTEL embeddings...")
            with open(cache_path, "r") as f:
                course_embeddings = json.load(f)
                # Re-convert to list of dicts if needed, or ensure the format is consistent
        else:
            logger.info("⚠️ Cache not found. Computing embeddings (slow)...")
            course_embeddings = course_embedding(nptel_data)
        
        logger.info("Embeddings Ready!")

        # Compute similarity score of "user syllabus" with "all available NPTEL courses"
        similarity_scores = computing_similarity(user_embedding, course_embeddings)
        
        logger.info("Similarity Computed!")

        # Write similarity scores to the output JSON file
        output_file_path = "artifacts/similarity_scores.json"
        with open(output_file_path, "w") as f:
            json.dump(similarity_scores, f, indent=4)

        # Get the top 8 relevant courses based on similarity scores
        top_8_courses = rate_courses(similarity_scores)

        # Load course metadata and retrieve info for the top courses
        course_data_path = "data/processed/final_data.csv"
        course_data = load_csv(course_data_path)

        # Merge course info with similarity scores
        formatted_courses = []
        for course in top_8_courses:
            course_id = course.get("course_id")
            course_similarity = course.get("similarity")
            course_info = get_course_info(course_data, course_id)
            if course_info:
                formatted_course = {
                    "id": course_info["id"],  # Course ID
                    "title": course_info["course name"],  # Course name
                    "instructors": course_info["sme name"],  # Instructors
                    "duration": course_info["duration"],  # Duration
                    "url": course_info["url"],  # Course URL
                    "similarity": course_similarity,  # Similarity score
                }
                formatted_courses.append(formatted_course)
        logger.info("Courses are ready to display!")
        logger.info(f"Courses: {formatted_courses}")

        return formatted_courses

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
        


from fastapi.responses import JSONResponse, FileResponse
from .utils.pdf_generator import generate_question_paper_pdf
from .utils.docx_generator import generate_question_paper_docx
from .utils.mcq_pdf_generator import generate_mcq_pdf
from .utils.mcq_docx_generator import generate_mcq_docx
from .utils.qb_pdf_generator import generate_question_bank_pdf
from .utils.qb_docx_generator import generate_question_bank_docx
import uuid

@app.post("/upload-question-paper")
async def upload_question_paper(
    question_papers: list[UploadFile] = File(...),
    threshold: float = Form(...),
    difficulty: str = Form("medium"),
    file_format: str = Form("pdf"),
    syllabus_file: UploadFile = File(None),
    include_answers: str = Form("false")
):
    try:
        include_ans_bool = include_answers.lower() == "true"
        UPLOAD_DIR = "artifacts/question_papers"
        UPLOAD_DIR = os.path.normpath(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        saved_files = []

        if syllabus_file:
            syllabus_path = os.path.join("artifacts", "College_Course_Syllabus.pdf")
            with open(syllabus_path, "wb") as f:
                shutil.copyfileobj(syllabus_file.file, f)

        for old_file in os.listdir(UPLOAD_DIR):
            if old_file.endswith(".pdf"):
                try:
                    os.remove(os.path.join(UPLOAD_DIR, old_file))
                except Exception as e:
                    print(f"Warning: Could not remove old file {old_file}: {e}")

        for file in question_papers:
            safe_filename = os.path.basename(file.filename)
            file_path = os.path.join(UPLOAD_DIR, safe_filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            saved_files.append(safe_filename)

        threshold_path = os.path.join(UPLOAD_DIR, "threshold.txt")
        with open(threshold_path, "w") as f:
            f.write(str(threshold))

        tutor = TutorVisionAPI()
        result = tutor.process_with_api(difficulty=difficulty, include_answers=include_ans_bool)
        
        file_url = None
        if result.get('success'):
            OUTPUT_DIR = os.path.join("artifacts", "generated")
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            if file_format == "docx":
                filename = f"generated_paper_{uuid.uuid4().hex[:8]}.docx"
                full_path = os.path.join(OUTPUT_DIR, filename)
                generate_question_paper_docx(result, full_path, difficulty=difficulty, include_answers=include_ans_bool)
            else:
                filename = f"generated_paper_{uuid.uuid4().hex[:8]}.pdf"
                full_path = os.path.join(OUTPUT_DIR, filename)
                generate_question_paper_pdf(result, full_path, difficulty=difficulty, include_answers=include_ans_bool)
            
            file_url = f"/download-file/{filename}"
            tutor.save_output(result=result)
        
        return JSONResponse(content={
                "message": "Question paper generated successfully!",
                "result": result,
                "file_url": file_url
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/generate-mcq")
async def generate_mcq(
    question_papers: list[UploadFile] = File(...),
    difficulty: str = Form("medium"),
    file_format: str = Form("pdf"),
    syllabus_file: UploadFile = File(None),
    include_answers: str = Form("false")
):
    try:
        include_ans_bool = include_answers.lower() == "true"
        UPLOAD_DIR = "artifacts/question_papers"
        UPLOAD_DIR = os.path.normpath(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        if syllabus_file:
            syllabus_path = os.path.join("artifacts", "College_Course_Syllabus.pdf")
            with open(syllabus_path, "wb") as f:
                shutil.copyfileobj(syllabus_file.file, f)

        # Clear old files
        for old_file in os.listdir(UPLOAD_DIR):
            if old_file.endswith(".pdf"):
                os.remove(os.path.join(UPLOAD_DIR, old_file))

        for file in question_papers:
            safe_filename = os.path.basename(file.filename)
            file_path = os.path.join(UPLOAD_DIR, safe_filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

        tutor = TutorVisionAPI()
        # MCQs always have answers in JSON, but we pass the flag for potential future use
        result = tutor.generate_mcq_with_api(difficulty=difficulty)
        
        file_url = None
        if result.get('success'):
            OUTPUT_DIR = os.path.join("artifacts", "generated")
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            if file_format == "docx":
                filename = f"mcq_paper_{uuid.uuid4().hex[:8]}.docx"
                full_path = os.path.join(OUTPUT_DIR, filename)
                generate_mcq_docx(result, full_path)
            else:
                filename = f"mcq_paper_{uuid.uuid4().hex[:8]}.pdf"
                full_path = os.path.join(OUTPUT_DIR, filename)
                generate_mcq_pdf(result, full_path)
            
            file_url = f"/download-file/{filename}"
        
        return JSONResponse(content={
                "message": "MCQ paper generated successfully!",
                "result": result,
                "file_url": file_url
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/analyze-trends")
async def analyze_trends():
    try:
        tutor = TutorVisionAPI()
        result = tutor.analyze_trends()
        return JSONResponse(content={
            "message": "Trends analyzed successfully!",
            "result": result
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/generate-question-bank")
async def generate_question_bank_endpoint(
    question_papers: list[UploadFile] = File(...),
    difficulty: int = Form(1),
    file_format: str = Form("pdf"),
    syllabus_file: UploadFile = File(...)
):
    try:
        UPLOAD_DIR = "artifacts/question_papers"
        UPLOAD_DIR = os.path.normpath(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Clear old papers
        for old_file in os.listdir(UPLOAD_DIR):
            if old_file.endswith(".pdf"):
                os.remove(os.path.join(UPLOAD_DIR, old_file))

        # Save Syllabus
        syllabus_path = os.path.join("artifacts", "College_Course_Syllabus.pdf")
        with open(syllabus_path, "wb") as f:
            shutil.copyfileobj(syllabus_file.file, f)

        # Save PYQs
        for file in question_papers:
            safe_filename = os.path.basename(file.filename)
            file_path = os.path.join(UPLOAD_DIR, safe_filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

        tutor = TutorVisionAPI()
        result = tutor.generate_question_bank(level=difficulty)
        
        file_url = None
        if result.get('success'):
            OUTPUT_DIR = os.path.join("artifacts", "generated")
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            if file_format == "docx":
                filename = f"question_bank_{uuid.uuid4().hex[:8]}.docx"
                full_path = os.path.join(OUTPUT_DIR, filename)
                generate_question_bank_docx(result, full_path)
            else:
                filename = f"question_bank_{uuid.uuid4().hex[:8]}.pdf"
                full_path = os.path.join(OUTPUT_DIR, filename)
                generate_question_bank_pdf(result, full_path)
            
            file_url = f"/download-file/{filename}"
            tutor.save_output(result=result)

        return JSONResponse(content={
                "message": "Question Bank generated successfully!",
                "result": result,
                "file_url": file_url
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/download-file/{filename}")
async def download_file(filename: str):
    file_path = os.path.join("artifacts", "generated", filename)
    if os.path.exists(file_path):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if filename.endswith(".docx") else "application/pdf"
        return FileResponse(
            file_path,
            media_type=media_type,
            filename=filename,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    return JSONResponse(status_code=404, content={"error": "File not found"})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
