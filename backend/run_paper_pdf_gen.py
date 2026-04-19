import os
import sys
import json
from pathlib import Path

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.utils.generate_paper import TutorVisionAPI
from src.utils.pdf_generator import generate_question_paper_pdf
from src.utils.docx_generator import generate_question_paper_docx

def main():
    print("Initializing TutorVision PDF Generator...")
    tutor = TutorVisionAPI()
    
    # Process and get the JSON result
    print("Generating question paper data (JSON)...")
    result = tutor.process_with_api(difficulty='medium', include_answers=True)
    
    if result.get('success'):
        print("✓ JSON Data generated successfully.")
        
        # Save JSON output for reference
        output_json = "artifacts/generated/testing_paper.json"
        os.makedirs("artifacts/generated", exist_ok=True)
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"✓ JSON saved to {output_json}")
        
        # Generate PDF
        output_pdf = "artifacts/generated/testing_paper.pdf"
        print(f"Generating PDF: {output_pdf}...")
        generate_question_paper_pdf(result, output_pdf, difficulty='medium', include_answers=True)
        print(f"✓ PDF generated successfully at {output_pdf}")
        
        # Generate DOCX as well
        output_docx = "artifacts/generated/testing_paper.docx"
        print(f"Generating DOCX: {output_docx}...")
        generate_question_paper_docx(result, output_docx, difficulty='medium', include_answers=True)
        print(f"✓ DOCX generated successfully at {output_docx}")
        
    else:
        print(f"Error generating paper: {result.get('error')}")

if __name__ == "__main__":
    main()
