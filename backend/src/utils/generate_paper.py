import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import PyPDF2
from pathlib import Path
import requests
import fitz
import base64
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

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
        
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.hf_api_key = os.environ.get("HF_API_KEY")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.cerebras_api_key = os.environ.get("CEREBRAS_API_KEY")
        self.together_api_key = os.environ.get("TOGETHER_API_KEY")
        
        # Count available engines
        available = sum(1 for k in [self.groq_api_key, self.gemini_api_key, self.hf_api_key, self.cerebras_api_key, self.together_api_key] if k)
        print(f"\n Using API Service: {self.use_service.upper()} ({available} engines available)")
        
    def extract_text_via_vision(self, base64_image):
        """Call Groq Vision API to extract text from a base64 image (OCR alternative)"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all text from this exam paper image accurately. Do not add any extra commentary or conversational filler. Only output the extracted text."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.2,
            "max_tokens": 2048
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"Vision API Error: {response.text}")
            return ""

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using PyMuPDF (much better at OCR'd and complex PDFs)"""
        try:
            text = ""
            doc = fitz.open(pdf_path)
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            doc.close()
            
            # If extracted text is very short (e.g. just a few characters/newlines), it's likely a scanned image
            if len(text.strip()) < 50 and self.groq_api_key and self.use_service == 'groq':
                # Vision model fallback disabled due to decommissioning, but left as stub for future models
                print(f"  [OCR-Warning] Very low text found in {Path(pdf_path).name}. If it's an image, please OCR it.")
            
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
        """Call Groq API with automatic fallback for Rate Limits (429)"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        # List of models to try in order of preference/strength
        models = [
            "llama-3.3-70b-versatile",
            "llama3-70b-8192",
            "llama-3.1-8b-instant"
        ]

        import time
        for attempt in range(2): # Two full passes through the model list
            for model in models:
                try:
                    print(f"   [Try Model: {model}]", flush=True)
                    data = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are an expert academic question paper generator."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.5,
                        "max_tokens": 4096
                    }
                    
                    response = requests.post(url, json=data, headers=headers)
                    
                    if response.status_code == 200:
                        return response.json()['choices'][0]['message']['content']
                    elif response.status_code == 429:
                        print(f"   ⚠️ Rate limited on {model}. Waiting 5s...")
                        time.sleep(5)
                        continue
                    elif response.status_code == 413:
                        print(f"   ⚠️ Prompt too large for {model}. Skipping to larger model...")
                        continue
                    elif response.status_code == 400 and "decommissioned" in response.text:
                        print(f"   ⚠️ {model} is decommissioned. Skipping...")
                        continue
                    else:
                        raise Exception(f"Groq {model} Error: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"   Error using {model}: {e}")
                    continue
            
            if attempt == 0:
                print("   😴 All models busy. Waiting 15s for rate limit reset...")
                time.sleep(15)

        raise Exception("All Groq models rate limited. Please wait 30-60 seconds and try again.")
    
    def call_huggingface_api(self, prompt):
        """Call HuggingFace Inference API via router (OpenAI-compatible chat format)"""
        import time
        
        # Models to try - each may have different availability
        hf_models = [
            "Qwen/Qwen2.5-72B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3",
        ]
        
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json"
        }
        
        for model in hf_models:
            # Use OpenAI-compatible chat completions format via router
            url = f"https://router.huggingface.co/hf-inference/models/{model}/v1/chat/completions"
            
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are an expert academic question paper generator."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 8000,
                "temperature": 0.5,
            }
            
            for attempt in range(2):
                try:
                    print(f"   [HF Model: {model}]", flush=True)
                    response = requests.post(url, json=data, headers=headers)
                    
                    if response.status_code == 200:
                        return response.json()['choices'][0]['message']['content']
                    elif response.status_code == 503:
                        wait_time = 30
                        try:
                            wait_time = response.json().get('estimated_time', 30)
                        except:
                            pass
                        print(f"   ⏳ HF model loading, waiting {wait_time:.0f}s...")
                        time.sleep(min(wait_time, 60))
                        continue
                    elif response.status_code == 403:
                        print(f"   ⚠️ HF permission denied for {model}. Trying next model...")
                        break  # Try next model
                    else:
                        print(f"   ⚠️ HF {model} Error: {response.status_code}")
                        break  # Try next model
                except Exception as e:
                    print(f"   Error with HF {model}: {e}")
                    break
        
        raise Exception("All HuggingFace models failed. Check your HF token permissions at https://huggingface.co/settings/tokens")

    def call_gemini_api(self, prompt, model="gemini-2.0-flash"):
        """Call Gemini API via REST with retry-after support for 429 errors"""
        import time
        import re
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts":[{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.5,
                "maxOutputTokens": 8000,
            }
        }
        
        for attempt in range(2):
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 429:
                # Parse retry delay from response
                retry_match = re.search(r'retry in (\d+\.?\d*)', response.text, re.IGNORECASE)
                wait_secs = float(retry_match.group(1)) if retry_match else 40
                wait_secs = min(wait_secs, 60)  # Cap at 60s
                if attempt == 0:
                    print(f"   ⏳ Gemini {model} rate limited. Waiting {wait_secs:.0f}s...")
                    time.sleep(wait_secs)
                    continue
                else:
                    raise Exception(f"Gemini {model} quota exhausted after retry.")
            else:
                raise Exception(f"Gemini {model} Error: {response.status_code} - {response.text}")
        
        raise Exception(f"Gemini {model} failed after retries.")

    def call_cerebras_api(self, prompt):
        """Call Cerebras API (OpenAI-compatible, very fast inference)"""
        url = "https://api.cerebras.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.cerebras_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b",
            "messages": [
                {"role": "system", "content": "You are an expert academic question paper generator."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_completion_tokens": 8192
        }
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        elif response.status_code == 429:
            raise Exception(f"Cerebras rate limited: {response.text[:200]}")
        else:
            raise Exception(f"Cerebras Error: {response.status_code} - {response.text[:300]}")

    def call_together_api(self, prompt):
        """Call Together AI API (OpenAI-compatible, many free models)"""
        import time
        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
            "Content-Type": "application/json"
        }
        
        # Models to try in order (free-tier compatible)
        models = [
            "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        ]
        
        for model in models:
            try:
                print(f"   [Together Model: {model.split('/')[-1]}]", flush=True)
                data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an expert academic question paper generator."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 8192
                }
                
                response = requests.post(url, json=data, headers=headers)
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content']
                elif response.status_code == 429:
                    print(f"   ⚠️ Together {model.split('/')[-1]} rate limited. Trying next...")
                    time.sleep(2)
                    continue
                else:
                    print(f"   ⚠️ Together {model.split('/')[-1]} Error: {response.status_code}")
                    continue
            except Exception as e:
                print(f"   Error with Together {model}: {e}")
                continue
        
        raise Exception("All Together AI models failed.")
    
    def generate_with_api(self, prompt):
        """Generate response using chosen API with multi-tier Failover"""
        print(f"\n Calling {self.use_service.upper()} API...")
        
        # Ordered list of all engines to try (fresh-quota engines first)
        engines = []
        
        if self.cerebras_api_key:
            engines.append(("cerebras", None))
        if self.together_api_key:
            engines.append(("together", None))
        if self.groq_api_key:
            engines.append(("groq", None))
        if self.gemini_api_key:
            engines.append(("gemini", "gemini-2.0-flash"))
            engines.append(("gemini", "gemini-2.0-flash-lite"))
        if self.hf_api_key:
            engines.append(("huggingface", None))
        
        errors = []
        for i, (engine, model) in enumerate(engines):
            try:
                label = f"{engine.upper()}" + (f" ({model})" if model else "")
                if i > 0:
                    print(f"\n   🔄 [FAILOVER {i}] Trying {label}...", flush=True)
                
                if engine == "groq":
                    return self.call_groq_api(prompt)
                elif engine == "cerebras":
                    return self.call_cerebras_api(prompt)
                elif engine == "gemini":
                    return self.call_gemini_api(prompt, model=model)
                elif engine == "together":
                    return self.call_together_api(prompt)
                elif engine == "huggingface":
                    return self.call_huggingface_api(prompt)
            except Exception as e:
                errors.append(f"{label}: {e}")
                print(f"   ❌ {label} failed: {e}")
                continue
        
        error_summary = "\n".join(errors)
        raise Exception(f"ALL ENGINES FAILED.\n{error_summary}")
    
    def process_with_api(self, difficulty='medium', include_answers=False):
        """Main processing - ONE API CALL DOES EVERYTHING"""
        
        # 1. Read all question papers
        pdf_files = list(self.base_dir.glob("*.pdf"))
        if not pdf_files:
            return {'error': 'No PDF files found'}
        
        papers_data = []
        for pdf_path in pdf_files:
            text = self.extract_text_from_pdf(pdf_path)
            year = self.get_year_from_filename(pdf_path.name)
            print(f"Extracted {len(text)} characters from {pdf_path.name}")
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
        
        prompt = f"""You are an expert question paper generator for academic exams.

**YOUR TASK:**
Analyze old question papers and syllabus, then generate an intelligent question paper of exactly 80 marks matching a university exam format.

**INPUTS:**

**Question Papers ({len(papers_data)} papers):**
"""
        
        for i, paper in enumerate(papers_data, 1):
            prompt += f"\n--- Paper {i}: {paper['filename']} (Year: {paper['year']}) ---\n"
            prompt += paper['content'][:1200] + "\n"
        
        prompt += f"""

**Syllabus:**
{syllabus_text}

---

**INSTRUCTIONS:**
    
Difficulty Level: {difficulty.upper()}
{{
  'easy': 'Focus on basic definitions, key terms, and foundational concepts. Avoid complex calculations. Questions should test direct recall and simple understanding.',
  'medium': 'Use a balanced mix of conceptual and applied questions. Include some straightforward calculations and comparison/explanation questions. Standard university exam style.',
  'hard': 'Use challenging analytical questions, complex multi-step calculations, case study evaluations, and questions that require critical reasoning and justification.'
}}.get(difficulty, '')

Generate exactly 6 main questions (Q1 to Q6), all compulsory to outline, following this strict criteria:

{f'''
- **Q1**: 20 Marks. You MUST provide the instruction "Choose the correct option". Supply EXACTLY 10 MCQs (labeled a to j), each worth 2 marks. The marks label MUST be exactly '20 (2x10)'. For each MCQ, provide the question in 'text', the marks as '2', and the 4 options (i, ii, iii, iv) in 'subparts'.
- **Q2**: 20 Marks. Provide an instruction "Answer any four". Supply 5 sub-questions (a, b, c, d, e), each worth 5 marks. Provide marks as '20 (4x5)'.
- **Q3**: 20 Marks. Provide two parts (a and b). Part 'a' MUST have an empty "text" field and NO "marks" field, but must contain two subparts (i and ii) worth 5 marks each. Part 'b' must be a single question worth 10 marks.
''' if difficulty.lower() == 'balanced' else '''
- **Q1**: 20 Marks. Provide an instruction "Answer any four". Supply 5 sub-questions (a, b, c, d, e), each worth 5 marks. Provide marks as '20 (4x5)'.
- **Q2**: 20 Marks. Provide two parts (a and b).
  - Part 'a' must have two subparts (i and ii) worth 5 marks each (total 10).
  - Part 'b' must be a single question worth 10 marks.
- **Q3**: 20 Marks. Provide exactly two parts (a and b), each being a single question worth 10 marks.
'''}
- **Q4 and Q5**: 20 Marks each. Provide exactly two parts (a and b), each being a single question worth 10 marks. (10 + 10 format).
- **Q6**: 20 Marks. Provide an instruction "Write short notes on any two". You MUST supply EXACTLY 4 short-note TOPIC NAMES (a, b, c, d) - use simple phrases/titles (e.g. "Project Risk Management") rather than full questions or explain-style sentences. Each topic is worth 10 marks. Provide marks as '20 (2x10)'.

Source {threshold}% of your questions by matching existing questions from the provided past papers (curating them based on frequency/importance), and create the remaining {100-threshold}% based heavily on the Syllabus text provided (AI-generated). Make sure ALL questions cover appropriate concepts.
Also, intelligently extract the main SUBJECT NAME or EXAM NAME (e.g. "Data Communications", "Software Engineering") based on the text context and provide it in the JSON.

**CRITICAL FORMATTING RULE:**
If a part (a, b, etc.) contains subparts (i, ii, etc.), the "text" and "marks" fields of that parent part MUST be empty strings (""). The marks and text should only reside within the subparts. Failure to do this ruins the document layout.

{f'''**MODEL ANSWER KEY INSTRUCTION:**
You MUST include an "answer_guide" field for every question-part and subpart. 
The "answer_guide" should be a string containing:
1. "Marking Scheme": How to distribute marks (e.g. 2 marks for definition, 3 marks for example).
2. "Key Points": 4-6 technical keywords or concepts that must be present.
Keep it concise but technical.''' if include_answers else ""}

**OUTPUT (Valid JSON only):**
{{
  "subject_name": "Operating Systems",
  "paper": [
    {{
      "qst_num": 1,
      "instruction": "Answer any four",
      "marks": "4x5",
      "parts": [
        {{"part_label": "a", "text": "Describe...", "marks": "5", "answer_guide": "Marking: 2 marks for def, 3 marks for key features. Key points: Scalability, Availability, Fault Tolerance."}},
        {{"part_label": "b", "text": "Differentiate...", "marks": "5", "answer_guide": "Marking: 2.5 marks for each difference. Key points: Latency vs Throughput, Vertical vs Horizontal scaling."}}
      ]
    }},
    {{
      "qst_num": 2,
      "instruction": "",
      "parts": [
        {{
          "part_label": "a", "text": "", "marks": "",
          "subparts": [
            {{"sub_label": "i", "text": "List and explain...", "marks": "5"}},
            {{"sub_label": "ii", "text": "What are...", "marks": "5"}}
          ]
        }},
        {{ "part_label": "b", "text": "Briefly list and define...", "marks": "10" }}
      ]
    }},
    {{
      "qst_num": 3,
      "instruction": "",
      "parts": [
        {{ "part_label": "a", "text": "Explain the process of...", "marks": "10" }},
        {{ "part_label": "b", "text": "Compare and contrast...", "marks": "10" }}
      ]
    }},
    {{
      "qst_num": 6,
      "instruction": "Write short notes on any two",
      "marks": "2x10",
      "parts": [
        {{"part_label": "a", "text": "Explain seven layers...", "marks": "10"}},
        {{"part_label": "b", "text": "Relate different techniques...", "marks": "10"}},
        {{"part_label": "c", "text": "Explain Automated...", "marks": "10"}},
        {{"part_label": "d", "text": "Discuss the advantages...", "marks": "10"}}
      ]
    }}
  ]
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
            
            # Use the shared robust parser
            result = self._clean_and_parse_json(response_text)
            return result
            
        except Exception as e:
            print(f" Error: {e}")
            return {'error': str(e)}

    def _clean_and_parse_json(self, response_text):
        """Robustly clean and parse AI-generated JSON string"""
        import re
        import ast
        
        response_text = response_text.strip()
        
        # 1. Clean up common AI prefixes/suffixes (markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        # 2. Extract only the portion between the first { and last }
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            response_text = response_text[start_idx:end_idx]
        
        # 3. Remove control characters (but preserve newlines for now)
        response_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1F\x7F]', '', response_text)
        
        # --- Attempt 1: Direct parse ---
        try:
            result = json.loads(response_text)
            result['success'] = True
            return result
        except json.JSONDecodeError:
            pass
        
        # --- Attempt 2: Fix trailing commas and retry ---
        try:
            fixed = re.sub(r',\s*([}\]])', r'\1', response_text)
            result = json.loads(fixed)
            result['success'] = True
            return result
        except json.JSONDecodeError:
            pass
        
        # --- Attempt 3: Single-quoted JSON (very common from LLMs) ---
        try:
            # ast.literal_eval handles Python-style dicts with single quotes
            result = ast.literal_eval(response_text)
            if isinstance(result, dict):
                result['success'] = True
                return result
        except (ValueError, SyntaxError):
            pass
        
        # --- Attempt 4: Replace single quotes with double quotes ---
        try:
            # Smart single-to-double quote conversion
            # Don't replace apostrophes inside words (e.g., "don't")
            sq_fixed = response_text
            # Replace trailing commas first
            sq_fixed = re.sub(r',\s*([}\]])', r'\1', sq_fixed)
            # Replace single quotes used as JSON delimiters
            sq_fixed = re.sub(r"(?<=[{\[,:])\s*'", ' "', sq_fixed)
            sq_fixed = re.sub(r"'\s*(?=[}\]:,])", '"', sq_fixed)
            # Handle the opening brace case
            sq_fixed = re.sub(r"^{\s*'", '{"', sq_fixed)
            
            result = json.loads(sq_fixed)
            result['success'] = True
            return result
        except json.JSONDecodeError:
            pass
        
        # --- Attempt 5: Fix missing commas and unescaped quotes ---
        try:
            fixed_text = response_text
            fixed_text = re.sub(r'}\s*{', '}, {', fixed_text)
            fixed_text = re.sub(r']\s*{', '], {', fixed_text)
            fixed_text = re.sub(r',\s*([}\]])', r'\1', fixed_text)
            
            result = json.loads(fixed_text)
            result['success'] = True
            return result
        except json.JSONDecodeError:
            pass
        
        # --- Attempt 6: Truncated JSON recovery ---
        try:
            fixed_text = re.sub(r',\s*([}\]])', r'\1', response_text)
            
            last_obj_end = fixed_text.rfind('}')
            if last_obj_end != -1:
                truncated_json = fixed_text[:last_obj_end+1]
                
                # Balance braces and brackets
                open_braces = truncated_json.count('{')
                close_braces = truncated_json.count('}')
                open_brackets = truncated_json.count('[')
                close_brackets = truncated_json.count(']')
                
                while open_brackets > close_brackets:
                    truncated_json += "]"
                    close_brackets += 1
                while open_braces > close_braces:
                    truncated_json += "}"
                    close_braces += 1
                
                result = json.loads(truncated_json)
                result['success'] = True
                return result
        except Exception as final_e:
            print(f"  [Final-Resort-Failed]: {final_e}")
        
        # Log the raw response for debugging
        print(f"  [RAW RESPONSE (first 500 chars)]: {response_text[:500]}")
        raise Exception("Failed to parse AI response even with aggressive cleaning.")

    def generate_mcq_with_api(self, difficulty='medium'):
        """Generate 40 MCQs instead of a standard paper"""
        pdf_files = list(self.base_dir.glob("*.pdf"))
        if not pdf_files:
            return {'error': 'No PDF files found'}
        
        papers_data = []
        for pdf_path in pdf_files:
            text = self.extract_text_from_pdf(pdf_path)
            papers_data.append({
                'filename': pdf_path.name,
                'content': text[:4000]
            })
            
        syllabus_text = ""
        if self.syllabus_path.exists():
            syllabus_text = self.extract_text_from_pdf(self.syllabus_path)[:3000]
            
        difficulty_instr = {
            'easy': 'Focus on basic definitions, key terms, and direct recall.',
            'medium': 'Use a balanced mix of conceptual and applied questions.',
            'hard': 'Use challenging analytical questions and case study evaluations.'
        }.get(difficulty.lower(), '')

        prompt = f"""You are an expert academic multiple-choice question generator.

**INPUTS:**

**Question Papers ({len(papers_data)} papers):**
"""
        for i, paper in enumerate(papers_data, 1):
            prompt += f"\n--- Paper {i}: {paper['filename']} ---\n{paper['content'][:2000]}\n"
            
        prompt += f"""
**Syllabus:**
{syllabus_text}

---

**INSTRUCTIONS:**

Difficulty Level: {difficulty.upper()}
{difficulty_instr}

Generate exactly 40 Multiple Choice Questions (MCQs).
- Each question must have exactly 4 options (A, B, C, D).
- Each question must have the correct answer specified.
- Intelligently extract the main SUBJECT NAME or EXAM NAME and provide it in the JSON.

**OUTPUT (Valid JSON only):**
{{
  "subject_name": "Project Management",
  "mcqs": [
    {{
      "qst_num": 1,
      "text": "What is the primary goal of project management?",
      "options": {{
        "A": "Maximizing profit",
        "B": "Achieving project objectives within constraints",
        "C": "Hiring the best team",
        "D": "Minimizing risk"
      }},
      "answer": "B",
      "marks": 2
    }}
  ]
}}

Output ONLY valid JSON. Start with {{ and end with }}"""

        try:
            response_text = self.generate_with_api(prompt)
            return self._clean_and_parse_json(response_text)
        except Exception as e:
            print(f" Error generating MCQ: {e}")
            return {'error': str(e)}
    
        print(f"\n Output saved to: {output_path}")
        return result

    def analyze_trends(self):
        """Analyze past papers against syllabus to find trends and weightage"""
        pdf_files = list(self.base_dir.glob("*.pdf"))
        if not pdf_files:
            return {'error': 'No PYQ files found'}
        
        papers_data = []
        for pdf_path in pdf_files:
            text = self.extract_text_from_pdf(pdf_path)
            papers_data.append({
                'filename': pdf_path.name,
                'content': text[:3000] # Use first 3000 chars for context
            })
            
        syllabus_text = ""
        if self.syllabus_path.exists():
            syllabus_text = self.extract_text_from_pdf(self.syllabus_path)[:4000]
            
        prompt = f"""You are an expert academic data analyst. Analyze the relationship between the provided Syllabus and the Past Question Papers (PYQs).

**INPUTS:**

**Syllabus:**
{syllabus_text}

**Past Papers ({len(papers_data)}):**
"""
        for i, paper in enumerate(papers_data, 1):
            prompt += f"\n--- Paper {i}: {paper['filename']} ---\n{paper['content'][:1800]}\n"
            
        prompt += """
---

**TASK:**
1. Identify the Modules/Units/Chapters from the syllabus.
2. For each Module, calculate its 'Exam Weightage' (frequency of questions in PYQs).
3. Identify 'High Priority Topics' (specific concepts asked in multiple years).
4. Identify 'Syllabus Gaps' (topics clearly mentioned in syllabus but never asked in these PYQs).
5. Generate a 'Study Roadmap' recommendation.

**OUTPUT (Valid JSON only):**
{
  "subject_name": "Subject Name",
  "modules": [
    { "name": "Module 1 Name", "weightage": 35, "question_count": 12 },
    { "name": "Module 2 Name", "weightage": 15, "question_count": 4 }
  ],
  "high_priority_topics": [
    { "topic": "Concept Name", "reason": "Asked in 2022, 2023, 2024" }
  ],
  "syllabus_gaps": [
    "Concept X from Module 4"
  ],
  "study_roadmap": [
    "Phase 1: Focus on Module 1 (Highest weightage)",
    "Phase 2: Master Topic Y..."
  ],
  "readiness_score": 85
}

Output ONLY valid JSON."""

        try:
            response_text = self.generate_with_api(prompt)
            return self._clean_and_parse_json(response_text)
        except Exception as e:
            print(f" Error analyzing trends: {e}")
            return {'error': str(e)}


    def save_output(self, result, output_path="output_paper_api.json"):
        """Save the generation result to a JSON file"""
        if not result:
            return None
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n Output saved to: {output_path}")
        return result

    def generate_question_bank(self, level=1):
        """Generate a structured Question Bank sorted by modules"""
        pdf_files = list(self.base_dir.glob("*.pdf"))
        
        papers_text = ""
        for pdf_path in pdf_files:
            text = self.extract_text_from_pdf(pdf_path)
            papers_text += f"\n--- PAPER: {pdf_path.name} ---\n{text[:2000]}\n"
            
        syllabus_text = ""
        if self.syllabus_path.exists():
            syllabus_text = self.extract_text_from_pdf(self.syllabus_path)[:4000]

        # Determine target question counts per module based on level
        counts = {1: "Total ~25-30 (Focus strictly on PYQs)", 2: "Total ~35 (Mix of PYQs and AI)", 3: "Total ~40-50 (Deep comprehensive coverage)"}
        target_count = counts.get(level, counts[1])

        prompt = f"""You are an academic expert. Create a QUESTION BANK for the following subject.

**Syllabus:**
{syllabus_text}

**Past Exam Content:**
{papers_text}

**TASK:**
1. Identify the Modules/Units from the syllabus.
2. For EACH Module, create a list of important questions.
3. GOAL: Ensure the TOTAL QUESTION COUNT for the entire bank is at least {target_count}. 
4. LEVEL: {level}. 
   - Level 1: Primarily use questions from Past Papers. Ensure EVERY module has at least 5-6 questions.
   - Level 2/3: Thoroughly extract ALL unique questions from the 6 past papers and add AI-generated questions to fill gaps until the total count hits the goal of {target_count}.
5. Each question must be descriptive and distinct.

**FORMAT (Strict JSON only):**
{{
  "subject_name": "Subject Name",
  "modules": [
    {{
      "name": "Module 1: Title",
      "questions": [
        "What is X and explain its working?",
        "Compare Y and Z..."
      ]
    }}
  ]
}}

Output ONLY the JSON."""

        try:
            response_text = self.generate_with_api(prompt)
            return self._clean_and_parse_json(response_text)
        except Exception as e:
            print(f" Error generating question bank: {e}")
            return {'error': str(e)}

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