import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import axios from 'axios';
import { Upload, FileText, X, TrendingUp } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const CourseAnalysis: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [selectedSyllabus, setSelectedSyllabus] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const handleSyllabusChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedSyllabus(e.target.files[0]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadAndAnalyze = async () => {
    if (selectedFiles.length === 0) {
      setError("Please select at least one PYQ to analyze.");
      return;
    }

    setIsUploading(true);
    setLoading(true);
    setError(null);

    const formData = new FormData();
    selectedFiles.forEach(file => {
      formData.append('question_papers', file);
    });
    if (selectedSyllabus) {
      formData.append('syllabus_file', selectedSyllabus);
    }
    formData.append('threshold', '30'); 

    try {
      // First, upload the files
      await axios.post('http://localhost:8000/upload-question-paper', formData);
      
      // Then, run the analysis
      const response = await axios.post('http://localhost:8000/analyze-trends');
      if (response.data.result.success) {
        setData(response.data.result);
      } else {
        setError(response.data.result.error || "Analysis failed");
      }
    } catch (err: any) {
      setError(err.response?.data?.error || "Connection error during upload/analysis");
    } finally {
      setIsUploading(false);
      setLoading(false);
    }
  };

  const chartData = data ? {
    labels: data.modules.map((m: any, i: number) => `Module ${i + 1}`),
    datasets: [
      {
        label: 'Exam Weightage (%)',
        data: data.modules.map((m: any) => m.weightage),
        backgroundColor: 'rgba(11, 87, 208, 0.7)',
        borderColor: 'rgb(11, 87, 208)',
        borderWidth: 1,
        borderRadius: 8,
      },
    ],
  } : null;

  const pieData = data ? {
    labels: data.modules.map((m: any, i: number) => `Module ${i + 1}`),
    datasets: [
      {
        data: data.modules.map((m: any) => m.question_count),
        backgroundColor: [
          '#0b57d0', '#1a73e8', '#4285f4', '#669df6', '#8ab4f8', '#aecbfa'
        ],
        borderWidth: 0,
      },
    ],
  } : null;

  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col md:flex-row gap-6 bg-[#f0f4f9] p-8 rounded-[2rem] shadow-sm border border-[#e3e2e6]">
        <div className="flex-1 space-y-4">
          <div>
            <h2 className="text-3xl font-bold text-[#1b1b1f] flex items-center gap-2">
              <TrendingUp className="text-[#0b57d0]" /> Academic Trends
            </h2>
            <p className="text-sm text-[#444746] mt-1">Upload past papers to discover module weightage and syllabus gaps.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
             {/* Syllabus Upload */}
             <div className="space-y-2">
                <p className="text-[10px] font-black uppercase text-[#0b57d0] tracking-widest pl-1">Target Syllabus</p>
                <label className={`flex items-center justify-between w-full p-4 border-2 border-dashed rounded-2xl cursor-pointer transition-all ${selectedSyllabus ? 'bg-blue-50 border-blue-400' : 'bg-white border-[#c4c7c5] hover:border-[#0b57d0]'}`}>
                   {!selectedSyllabus ? (
                      <div className="flex items-center gap-2">
                         <Upload size={16} className="text-[#444746]" />
                         <span className="text-xs font-bold text-[#444746]">Add Subject Syllabus</span>
                      </div>
                   ) : (
                      <div className="flex items-center gap-2 overflow-hidden">
                         <FileText size={16} className="text-[#0b57d0]" />
                         <span className="text-xs font-bold text-[#0b57d0] truncate">{selectedSyllabus.name}</span>
                      </div>
                   )}
                   <input type="file" className="hidden" onChange={handleSyllabusChange} accept=".pdf" />
                </label>
             </div>

             {/* PYQ Upload */}
                <label className="flex items-center justify-between w-full p-4 border-2 border-dashed border-[#c4c7c5] rounded-2xl cursor-pointer bg-white hover:bg-[#f8f9fa] hover:border-[#0b57d0] transition-all">
                    <div className="flex items-center gap-2">
                      <Upload size={16} className="text-[#444746]" />
                      <span className="text-xs font-bold text-[#444746]">Add PYQs</span>
                    </div>
                    {selectedFiles.length > 0 && <span className="bg-blue-100 text-blue-700 text-[10px] px-2 py-0.5 rounded-full font-bold">{selectedFiles.length} Added</span>}
                    <input type="file" multiple className="hidden" onChange={handleFileChange} accept=".pdf" />
                </label>

          </div>

          {selectedFiles.length > 0 && !data && (
                <div className="bg-white/50 rounded-xl p-3 max-h-32 overflow-y-auto border border-[#e3e2e6]">
                   {selectedFiles.map((file, i) => (
                      <div key={i} className="flex justify-between items-center text-xs py-1 border-b border-[#f0f0f0] last:border-0 text-[#444746]">
                         <span className="flex items-center gap-2"><FileText size={12} /> {file.name}</span>
                         <button onClick={() => removeFile(i)} className="text-[#b3261e] hover:bg-red-50 p-1 rounded"><X size={12} /></button>
                      </div>
                   ))}
                </div>
             )}


          {!data && !loading && (
            <button
              onClick={uploadAndAnalyze}
              disabled={selectedFiles.length === 0}
              className={`w-full py-3 rounded-xl font-bold transition-all shadow-md active:scale-[0.98] ${
                selectedFiles.length > 0 
                ? "bg-[#0b57d0] text-white hover:bg-[#0842a0]" 
                : "bg-[#c4c7c5] text-white cursor-not-allowed opacity-50"
              }`}
            >
              Start Analysis
            </button>
          )}
        </div>
        
        <div className="w-full md:w-64 bg-white/40 border border-white rounded-[1.5rem] p-6 flex flex-col justify-center items-center text-center space-y-3">
          <div className="bg-blue-100 p-4 rounded-full">
             <TrendingUp className="text-[#0b57d0]" size={32} />
          </div>
          <p className="text-xs text-[#444746] leading-relaxed">
            AI will map every question to your syllabus units to find hidden trends.
          </p>
        </div>
      </div>

      {loading && (
        <div className="flex flex-col items-center justify-center py-20 space-y-4">
          <div className="w-12 h-12 border-4 border-[#0b57d0] border-t-transparent rounded-full animate-spin"></div>
          <p className="text-[#444746] animate-pulse font-medium">
            {isUploading ? "Uploading Papers..." : "Scanning PYQs and Mapping Syllabus..."}
          </p>
        </div>
      )}

      {error && (
        <div className="bg-[#f9dedc] text-[#410e0b] p-6 rounded-2xl border border-[#f2b8b5] flex justify-between items-center">
          <div>
            <h3 className="font-bold mb-1">Analysis Interrupted</h3>
            <p className="text-sm">{error}</p>
          </div>
          <button onClick={uploadAndAnalyze} className="text-sm font-bold bg-[#b3261e] text-white px-4 py-2 rounded-lg">Retry</button>
        </div>
      )}

      {data && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
        >
          {/* Module Weightage Chart */}
          <div className="bg-white p-6 rounded-3xl border border-[#e3e2e6] shadow-sm space-y-4">
            <h3 className="text-lg font-bold text-[#1b1b1f]">Module Weightage</h3>
            {chartData && (
              <Bar 
                data={chartData} 
                options={{ 
                  responsive: true, 
                  plugins: { 
                    legend: { display: false },
                    tooltip: {
                      callbacks: {
                        label: (context) => {
                          const module = data.modules[context.dataIndex];
                          return [`${module.name}`, `Weightage: ${context.parsed.y}%`];
                        }
                      }
                    }
                  },
                  scales: {
                    x: {
                      ticks: {
                        autoSkip: false,
                        maxRotation: 0,
                        minRotation: 0
                      }
                    }
                  }
                }} 
              />
            )}
          </div>

          {/* Question Distribution */}
          <div className="bg-white p-6 rounded-3xl border border-[#e3e2e6] shadow-sm space-y-4">
            <h3 className="text-lg font-bold text-[#1b1b1f]">Question Frequency</h3>
            <div className="max-w-[200px] mx-auto">
              {pieData && <Pie data={pieData} />}
            </div>
          </div>

          {/* High Priority Topics */}
          <div className="bg-gradient-to-br from-[#e3eefc] to-[#ffffff] p-8 rounded-3xl border border-[#d3e3fd] shadow-sm space-y-4">
            <h3 className="text-lg font-black text-[#0b57d0] flex items-center gap-2">
              <span className="text-2xl">🔥</span> High Priority Topics
            </h3>
            <ul className="space-y-4">
              {data.high_priority_topics.map((item: any, i: number) => (
                <li key={i} className="bg-white/60 p-3 rounded-xl border border-blue-100">
                  <span className="font-bold block text-[#1b1b1f]">{item.topic}</span>
                  <span className="text-xs text-[#444746]">{item.reason}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Syllabus Gaps */}
          <div className="bg-gradient-to-br from-[#fdf2f2] to-[#ffffff] p-8 rounded-3xl border border-[#f9dedc] shadow-sm space-y-4">
            <h3 className="text-lg font-black text-[#410e0b] flex items-center gap-2">
              <span className="text-2xl">⚡</span> Syllabus Gaps
            </h3>
            <p className="text-xs text-[#444746] mb-4">Topics in syllabus but never/rarely asked in these PYQs.</p>
            <ul className="space-y-2">
              {data.syllabus_gaps.map((gap: string, i: number) => (
                <li key={i} className="flex items-center gap-2 text-sm text-[#444746]">
                   <span className="w-1.5 h-1.5 bg-[#b3261e] rounded-full"></span>
                   {gap}
                </li>
              ))}
            </ul>
          </div>

          {/* Roadmap */}
          <div className="col-span-1 md:col-span-2 bg-[#1b1b1f] text-white p-8 rounded-3xl shadow-xl space-y-6">
            <h3 className="text-xl font-bold flex items-center gap-2">
              <span className="text-2xl">🛣️</span> AI Study Roadmap
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {data.study_roadmap.map((step: string, i: number) => (
                <div key={i} className="bg-[#2a2a2e] p-4 rounded-2xl border border-white/10 relative overflow-hidden">
                  <span className="absolute -right-2 -top-2 text-4xl font-black text-white/5">{i+1}</span>
                  <p className="text-sm leading-relaxed">{step}</p>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default CourseAnalysis;
