import json
import os
from sentence_transformers import SentenceTransformer
import time

def precompute_nptel_embeddings():
    print("Starting NPTEL Embedding Pre-computation...")
    start_time = time.time()
    
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))
    json_file_path = os.path.join(project_root, "data_scrape/cleaned_scraped.json")
    output_file_path = os.path.join(project_root, "artifacts/nptel_course_embeddings.json")
    
    if not os.path.exists(json_file_path):
        print(f"Error: {json_file_path} not found!")
        return

    # Load data
    with open(json_file_path, 'r') as file:
        nptel_data = json.load(file)
    
    print(f"Loaded {len(nptel_data)} courses. Initializing AI Model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Generating Embeddings (this takes a moment)...")
    course_embeddings = []
    for i, course in enumerate(nptel_data):
        if i % 50 == 0 and i > 0:
            print(f"   Processed {i}/{len(nptel_data)} courses...")
            
        embedding = model.encode(course["text"], convert_to_tensor=False)
        course_embeddings.append({
            "id": course["id"],
            "embedding": embedding.tolist() # Convert numpy array to list for JSON
        })
    
    # Ensure output dir exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    # Save
    with open(output_file_path, "w") as f:
        json.dump(course_embeddings, f)
        
    end_time = time.time()
    print(f"Success! Pre-computed embeddings saved to {output_file_path}")
    print(f"Total time taken: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    precompute_nptel_embeddings()
