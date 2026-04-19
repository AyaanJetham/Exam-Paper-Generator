import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, X, Database, Download, BookOpen, AlertCircle } from 'lucide-react';
import axios from 'axios';

const QuestionBank: React.FC = () => {
  const [syllabus, setSyllabus] = useState<File | null>(null);
  const [pyqs, setPyqs] = useState<File[]>([]);
  const [difficulty, setDifficulty] = useState<number>(1);
  const [fileFormat, setFileFormat] = useState<'pdf' | 'docx'>('pdf');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [fileUrl, setFileUrl] = useState<string | null>(null);

  const handleSyllabusChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setSyllabus(e.target.files[0]);
  };

  const handlePyqChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setPyqs(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removePyq = (index: number) => {
    setPyqs(prev => prev.filter((_, i) => i !== index));
  };

  const generateBank = async () => {
    if (!syllabus || pyqs.length === 0) {
      setError("Please upload syllabus and at least one PYQ.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setFileUrl(null);

    const formData = new FormData();
    formData.append('syllabus_file', syllabus);
    pyqs.forEach(file => formData.append('question_papers', file));
    formData.append('difficulty', difficulty.toString());
    formData.append('file_format', fileFormat);

    try {
      const resp = await axios.post('http://localhost:8000/generate-question-bank', formData);
      if (resp.data.result.success) {
        setResult(resp.data.result);
        setFileUrl(resp.data.file_url);
      } else {
        setError(resp.data.result.error || "Generation failed");
      }
    } catch (err: any) {
      setError(err.response?.data?.error || "Connection error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 pb-20">
      <div className="bg-white p-8 rounded-[2.5rem] border border-[#e3e2e6] shadow-sm space-y-8">
        <div className="flex items-center gap-4">
          <div className="bg-[#0b57d0] p-4 rounded-2xl shadow-lg shadow-blue-100 text-white">
            <Database size={28} />
          </div>
          <div>
            <h2 className="text-3xl font-black text-[#1b1b1f]">Smart Question Bank</h2>
            <p className="text-sm text-[#444746] mt-1">Generate a module-wise repository of academic questions.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Syllabus Section */}
          <div className="space-y-4">
            <h3 className="text-sm font-black uppercase text-[#0b57d0] tracking-widest pl-1">Course Syllabus</h3>
            <label className={`flex flex-col items-center justify-center h-48 border-2 border-dashed rounded-3xl cursor-pointer transition-all ${syllabus ? 'bg-blue-50 border-blue-400' : 'bg-[#f8f9fa] border-[#c4c7c5] hover:border-[#0b57d0]'}`}>
               {!syllabus ? (
                 <>
                   <Upload className="w-10 h-10 text-[#444746] mb-3" />
                   <p className="text-xs font-bold text-[#444746]">Upload Syllabus PDF</p>
                 </>
               ) : (
                 <div className="flex flex-col items-center p-4">
                   <FileText size={40} className="text-[#0b57d0] mb-3" />
                   <span className="text-xs font-bold text-[#0b57d0] text-center max-w-[150px] truncate">{syllabus.name}</span>
                   <button onClick={(e) => {e.preventDefault(); setSyllabus(null)}} className="mt-4 text-[10px] text-red-600 font-bold underline">Replace File</button>
                 </div>
               )}
               <input type="file" className="hidden" onChange={handleSyllabusChange} accept=".pdf" />
            </label>
          </div>

          {/* PYQ Section */}
          <div className="space-y-4">
             <h3 className="text-sm font-black uppercase text-[#0b57d0] tracking-widest pl-1">Past Exam Papers</h3>
             <div className="flex flex-col h-48 border-2 border-dashed border-[#c4c7c5] rounded-3xl bg-[#f8f9fa] overflow-hidden">
                <label className="flex items-center justify-center p-4 hover:bg-white cursor-pointer transition-all border-b border-[#e3e2e6]">
                   <div className="flex items-center gap-2">
                      <Upload size={16} className="text-[#0b57d0]" />
                      <span className="text-xs font-bold text-[#0b57d0]">Add PYQ PDFs</span>
                   </div>
                   <input type="file" multiple className="hidden" onChange={handlePyqChange} accept=".pdf" />
                </label>
                <div className="flex-1 p-4 overflow-y-auto space-y-2">
                   {pyqs.length === 0 ? (
                     <p className="text-[11px] text-[#444746] text-center mt-6">No papers added yet.</p>
                   ) : (
                     pyqs.map((file, i) => (
                       <div key={i} className="flex justify-between items-center bg-white p-2 rounded-xl text-[11px] border border-[#e3e2e6]">
                          <span className="truncate max-w-[150px]">{file.name}</span>
                          <X size={14} className="text-red-500 cursor-pointer" onClick={() => removePyq(i)} />
                       </div>
                     ))
                   )}
                </div>
             </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 border-t border-[#f0f0f0]">
          {/* Difficulty Selection */}
          <div className="space-y-3">
             <p className="text-xs font-black text-[#1b1b1f] uppercase tracking-wider">Target Level</p>
             <div className="flex gap-2">
                {[1, 2, 3].map(lvl => (
                  <button
                    key={lvl}
                    onClick={() => setDifficulty(lvl)}
                    className={`flex-1 py-3 rounded-2xl font-black text-sm transition-all ${difficulty === lvl ? 'bg-[#0b57d0] text-white shadow-md' : 'bg-[#f0f4f9] text-[#444746] hover:bg-[#e3e2e6]'}`}
                  >
                    L{lvl}
                  </button>
                ))}
             </div>
             <p className="text-[10px] text-[#444746] italic">
               {difficulty === 1 ? "PYQs Only + Critical Gaps" : difficulty === 2 ? "Extended (PYQs + 10x per module)" : "Full Coverage (Comprehensive)"}
             </p>
          </div>

          {/* Format Selection */}
          <div className="space-y-3">
             <p className="text-xs font-black text-[#1b1b1f] uppercase tracking-wider">Export Format</p>
             <div className="flex gap-2">
                {['pdf', 'docx'].map(fmt => (
                  <button
                    key={fmt}
                    onClick={() => setFileFormat(fmt as any)}
                    className={`flex-1 py-3 rounded-2xl font-black text-sm uppercase transition-all ${fileFormat === fmt ? 'bg-[#1b1b1f] text-white' : 'bg-[#f0f4f9] text-[#444746] hover:bg-[#e3e2e6]'}`}
                  >
                    {fmt}
                  </button>
                ))}
             </div>
          </div>

          <div className="flex items-end">
            <button
               onClick={generateBank}
               disabled={loading || !syllabus || pyqs.length === 0}
               className={`w-full py-6 rounded-[2rem] font-black text-xl flex items-center justify-center gap-3 transition-all active:scale-95 shadow-xl ${loading ? 'bg-[#f0f4f9] text-[#0b57d0]' : 'bg-[#0b57d0] text-white hover:bg-[#0842a0] shadow-blue-100'}`}
            >
               {loading ? (
                 <>
                   <div className="w-5 h-5 border-2 border-t-transparent border-[#0b57d0] rounded-full animate-spin"></div>
                   Curating...
                 </>
               ) : (
                 <>
                   <BookOpen size={24} /> Generate Bank
                 </>
               )}
            </button>
          </div>
        </div>

        <AnimatePresence>
          {error && (
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="bg-red-50 text-red-700 p-4 rounded-2xl flex items-center gap-3 text-sm font-bold border border-red-100">
               <AlertCircle size={18} /> {error}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <div className="bg-[#1b1b1f] text-white p-8 rounded-[2.5rem] flex flex-col md:flex-row justify-between items-center gap-6 shadow-2xl overflow-hidden relative">
             <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32"></div>
             <div className="space-y-1 relative">
                <h3 className="text-2xl font-black">Question Bank Ready</h3>
                <p className="text-gray-400 text-sm">Successfully curated {result.modules.length} modules for {result.subject_name}.</p>
             </div>
             <button
                onClick={async () => {
                  try {
                    const res = await fetch(`http://localhost:8000${fileUrl}`);
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    const fileName = fileUrl!.split("/").pop() || `question_bank.${fileFormat}`;
                    a.download = fileName;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
                  } catch (err) {
                    console.error("Download failed:", err);
                  }
                }}
                className="bg-white text-[#1b1b1f] px-10 py-5 rounded-3xl font-black text-lg flex items-center gap-3 hover:bg-gray-100 transition-all shadow-xl active:scale-95 relative cursor-pointer"
              >
                <Download size={24} /> Download {fileFormat.toUpperCase()}
              </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.modules.map((m: any, i: number) => (
              <div key={i} className="bg-white p-6 rounded-3xl border border-[#e3e2e6] shadow-sm">
                <h4 className="font-black text-[#0b57d0] mb-3 flex items-center gap-2">
                  <span className="text-[10px] bg-blue-100 px-2 py-0.5 rounded-full">UNIT {i+1}</span>
                  {m.name}
                </h4>
                <div className="text-xs text-[#444746] space-y-2">
                  {m.questions.slice(0, 3).map((q: string, j: number) => (
                    <p key={j} className="line-clamp-1 opacity-70">• {q}</p>
                  ))}
                  {m.questions.length > 3 && <p className="font-bold text-[#0b57d0] mt-2">+ {m.questions.length - 3} more questions</p>}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default QuestionBank;
