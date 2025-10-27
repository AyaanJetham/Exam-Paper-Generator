import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import PyPDF2
from pathlib import Path
import requests

class TutorVisionAPI:
    """
    Lightweight version using free API services
    Choose one: HuggingFace Inference API (free) or Groq (fast & free)
    """
    
    def __init__(self, base_dir="artifacts/question_papers"):
        self.base_dir = Path(base_dir)
        self.syllabus_path = Path("artifacts/College_Course_Syllabus.pdf")
        self.threshold_path = Path("artifacts/question_papers/threshold.txt")
        
        self.use_service = "groq"  
        
        self.groq_api_key = "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"
        self.hf_api_key = os.environ.get("HF_API_KEY", "")
        
        print(f"\n Using API Service: {self.use_service.upper()}")
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
    
    def read_threshold(self):
        """Read threshold from file"""
        try:
            if self.threshold_path.exists():
                with open(self.threshold_path, 'r') as f:
                    threshold = int(f.read().strip())
                    print(f"✓ Threshold: {threshold}%")
                    return threshold
        except:
            pass
        print("✓ Using default threshold: 30%")
        return 30
    
    def get_year_from_filename(self, filename):
        """Extract year from filename"""
        import re
        match = re.search(r'(MAY|DEC|JAN|APR)(\d{2})', filename)
        if match:
            year_short = int(match.group(2))
            return 2000 + year_short if year_short < 50 else 1900 + year_short
        
        match = re.search(r'20\d{2}', filename)
        if match:
            return int(match.group())
        
        return None
    
    def call_groq_api(self, prompt):
        """Call Groq API (Fast & Free)"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",  # Fast and smart
            "messages": [
                {"role": "system", "content": "You are an expert academic question paper generator."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 6000
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def call_huggingface_api(self, prompt):
        """Call HuggingFace Inference API (Free)"""
        url = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-72B-Instruct"
        
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}"
        }
        
        data = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 4000,
                "temperature": 0.5,
                "return_full_text": False
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()[0]['generated_text']
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def generate_with_api(self, prompt):
        """Generate response using chosen API"""
        print(f"\n Calling {self.use_service.upper()} API...")
        
        if self.use_service == "groq":
            if not self.groq_api_key:
                raise Exception("GROQ_API_KEY not set! Get free key at: https://console.groq.com")
            return self.call_groq_api(prompt)
        
        elif self.use_service == "huggingface":
            if not self.hf_api_key:
                raise Exception("HF_API_KEY not set! Get free key at: https://huggingface.co/settings/tokens")
            return self.call_huggingface_api(prompt)
    
    def process_with_api(self):
        """Main processing - ONE API CALL DOES EVERYTHING"""
        
        # 1. Read all question papers
        pdf_files = list(self.base_dir.glob("*.pdf"))
        if not pdf_files:
            return {'error': 'No PDF files found'}
        
        papers_data = []
        for pdf_path in pdf_files:
            text = self.extract_text_from_pdf(pdf_path)
            year = self.get_year_from_filename(pdf_path.name)
            papers_data.append({
                'filename': pdf_path.name,
                'year': year,
                'content': text[:4000]
            })
        
        # 2. Read syllabus
        syllabus_text = ""
        if self.syllabus_path.exists():
            syllabus_text = self.extract_text_from_pdf(self.syllabus_path)[:3000]
        
        # 3. Read threshold
        threshold = self.read_threshold()
        
        # 4. Create prompt
        prompt = f"""You are an expert question paper generator for academic exams.

**YOUR TASK:**
Analyze old question papers and syllabus, then generate an intelligent question paper.

**INPUTS:**

**Question Papers ({len(papers_data)} papers):**
"""
        
        for i, paper in enumerate(papers_data, 1):
            prompt += f"\n--- Paper {i}: {paper['filename']} (Year: {paper['year']}) ---\n"
            prompt += paper['content'][:2000] + "\n"
        
        prompt += f"""

**Syllabus:**
{syllabus_text}

**Threshold:** {threshold}%

---

**INSTRUCTIONS:**

1. Extract ALL questions from papers (ignore headers/instructions)
2. Group similar questions and calculate importance:
   - Frequency (50%): Times appeared
   - Recency (30%): Newer = higher score
   - Diversity (20%): Different years
3. Select top {threshold}% curated questions
4. Generate {100-threshold}% NEW questions from syllabus

**OUTPUT (Valid JSON only):**
{{
  "analysis": {{
    "total_questions_found": 20,
    "unique_question_groups": 18,
    "papers_analyzed": [{{"filename": "MAY18.pdf", "year": 2018, "questions_extracted": 10}}]
  }},
  "curated_questions": [
    {{
      "number": 1,
      "question": "Complete question text",
      "frequency": 2,
      "years_appeared": [2018, 2019],
      "importance_score": 85.5,
      "marks": 10
    }}
  ],
  "ai_generated_questions": [
    {{
      "number": 1,
      "question": "Complete question text",
      "syllabus_topic": "Topic from syllabus",
      "difficulty": "medium",
      "marks": 10
    }}
  ],
  "summary": {{
    "threshold_used": {threshold},
    "curated_count": 6,
    "ai_generated_count": 14,
    "total_questions": 20
  }}
}}

Output ONLY valid JSON. Start with {{ and end with }}"""

        print(f"\n Processing:")
        print(f"   Papers: {len(papers_data)}")
        print(f"   Threshold: {threshold}%")
        print(f"   Syllabus: {'Found' if syllabus_text else 'Not found'}")
        
        # 5. Call API
        try:
            response_text = self.generate_with_api(prompt)
            
            print(f"\n✓ Response received ({len(response_text)} chars)")
            
            # Parse JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
            
            result = json.loads(response_text.strip())
            result['success'] = True
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {
                'error': 'Failed to parse response',
                'raw_response': response_text[:1000]
            }
        except Exception as e:
            print(f" Error: {e}")
            return {'error': str(e)}
    
    def save_output(self, output_path="output_paper_api.json"):
        """Process and save output"""
        result = self.process_with_api()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, indent=2, fp=f, ensure_ascii=False)
        
        print(f"\n Output saved to: {output_path}")
        return result


# Usage
if __name__ == "__main__":
    print("\n" + "="*70)
    print("TUTOR VISION - API-BASED QUESTION PAPER GENERATOR")
    print("="*70)
    print("\n Setup Instructions:")
    print("   1. Groq (Recommended - Fast & Free):")
    print("      - Get key: https://console.groq.com")
    print("      - Set: export GROQ_API_KEY='your-key'")
    print("\n   2. HuggingFace (Alternative):")
    print("      - Get key: https://huggingface.co/settings/tokens")
    print("      - Set: export HF_API_KEY='your-key'")
    print("="*70)
    
    tutor = TutorVisionAPI()
    result = tutor.process_with_api()
    
    if result.get('success'):
        summary = result.get('summary', {})
        
        print(f"\n SUCCESS!")
        print(f"\n SUMMARY:")
        print(f"  Total: {summary.get('total_questions', 0)}")
        print(f"  Curated: {summary.get('curated_count', 0)}")
        print(f"  AI-Generated: {summary.get('ai_generated_count', 0)}")
        
        print(f"\n CURATED QUESTIONS:")
        for q in result.get('curated_questions', [])[:3]:
            print(f"\nQ{q['number']}. {q['question'][:100]}...")
            print(f"   {q['frequency']}x | {q['years_appeared']} | {q['importance_score']}%")
        
        print(f"\n AI-GENERATED:")
        for q in result.get('ai_generated_questions', [])[:3]:
            print(f"\nQ{q['number']}. {q['question'][:100]}...")
            print(f" {q['syllabus_topic']}")
        
        tutor.save_output()
        
    else:
        print(f"\nError: {result.get('error')}")
    
    print("\n" + "="*70)