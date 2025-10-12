from fastapi import FastAPI, File, UploadFile, File, Form
from user_syllabus_processing.extract_from_pdf import extract_module_content
from user_syllabus_processing.syllabus_preprocessing import preprocess_text
from generating_embeddings.user_embedding import user_syllabus_embedding
from generating_embeddings.course_embedding import course_embedding
from similarity.matching import computing_similarity
from similarity.rating import rate_courses
from similarity.get_course import get_course_info, load_csv
from fastapi.middleware.cors import CORSMiddleware
from getResources.extract import extract_keywords
from getResources.search import search_courses_on_google
from getResources.ranking import rank_search_results
from utils.logger import Logger
import os
from werkzeug.utils import secure_filename
import json
import shutil  # For better file handling
import uvicorn
from fastapi.responses import JSONResponse
import os
import shutil

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
      
        # Load NPTEL course data
        json_file_path = "data_scrape/cleaned_scraped.json"
        with open(json_file_path, 'r') as file:
            nptel_data = json.load(file)

        # Compute embeddings for NPTEL courses
        course_embeddings = course_embedding(nptel_data)
        
        logger.info("Emebeddings Created!")

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
        
@app.post("/get_resources")
async def get_resource():
    if not uploaded_file_path:
        return JSONResponse(status_code=400, content={"error": "No file uploaded."})

    try:
        # Extract module content from the uploaded PDF
        module_content = extract_module_content(uploaded_file_path)
        
        logger.info(f"Extracted Content: {module_content}")

        # Preprocess the text and extract keywords for the search query
        processed_content = preprocess_text(module_content)  # User PDF syllabus
        logger.info(f"After preprocessing: {processed_content}")

        keywords = extract_keywords(processed_content)
        query = " ".join(keywords)  # Create a more concise query from the keywords
        print("Query being searched:", query)
        logger.info(f"Query being searched: {query}")

        # Search for resources on Google
        resources = search_courses_on_google(query)
        if not resources:
            return JSONResponse(status_code=404, content={"error": "No resources found."})

        # Rank the search results using cosine similarity
        ranked_results = rank_search_results(processed_content, resources)

        # Format the ranked results for the response
        formatted_results = [
            {
                "title": result["title"],
                "link": result["link"],
                "snippet": result["snippet"],
                "relevance_score": score,
            }
            for score, result in ranked_results
        ]
        logger.info("Results are ready!")
        
        logger.info(f"Results: {formatted_results}")

        return {"resources": formatted_results}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/upload-question-paper")
async def upload_question_paper(
    question_papers: list[UploadFile] = File(...),
    threshold: float = Form(...)
):
    try:
        UPLOAD_DIR = "artifacts/question_papers"
        # Use os.path.normpath to ensure consistent path separators
        UPLOAD_DIR = os.path.normpath(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        saved_files = []

        for file in question_papers:
            # Sanitize filename to prevent directory traversal
            safe_filename = os.path.basename(file.filename)
            file_path = os.path.join(UPLOAD_DIR, safe_filename)
            
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            saved_files.append(safe_filename)

        # Save threshold value
        threshold_path = os.path.join(UPLOAD_DIR, "threshold.txt")
        with open(threshold_path, "w") as f:
            f.write(str(threshold))

        return JSONResponse(content={
            "message": "Question papers uploaded successfully!",
            "saved_files": saved_files,
            "threshold": threshold
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
