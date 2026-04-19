import React, { useState } from 'react';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import Results from './components/Results';
import { motion, AnimatePresence } from 'framer-motion';
import { uploadPDF, getCourses } from './services/api';
import SetQuestionPaper from './components/SetQuestionPaper';
import MCQPaper from './components/MCQPaper';
import CourseAnalysis from './components/CourseAnalysis';
import QuestionBank from './components/QuestionBank';
import { Database } from 'lucide-react';

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [courses, setCourses] = useState<any[]>([]);
  const [loadingCourses, setLoadingCourses] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'courses' | 'set-question-paper' | 'mcq-generator' | 'course-analysis' | 'question-bank'>('set-question-paper');

  const handleFileUpload = async (uploadedFile: File) => {
    setFile(uploadedFile);
    setError(null);
    try {
      await uploadPDF(uploadedFile);
    } catch (err) {
      setError('Error uploading file. Please try again.');
      console.error(err);
    }
  };

  const handleGetCourses = async () => {
    setLoadingCourses(true);
    setError(null);
    try {
      const coursesData = await getCourses();
      setCourses(coursesData);
      setActiveTab('courses');
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error || 'Unexpected error occurred. Please try again.';
      setError(errorMessage);
      console.error(err);
    } finally {
      setLoadingCourses(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fcfcff] font-sans text-[#1b1b1f] selection:bg-[#d3e3fd] selection:text-[#041e49] transition-colors duration-300">
      <Header />
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mb-8"
        >
          <div className="bg-[#f0f4f9] rounded-3xl p-8 mb-6">
            <h2 className="text-2xl font-medium text-[#1b1b1f] mb-6">
              Syllabus Uplink
            </h2>
            <div className="bg-white rounded-2xl p-4 shadow-[0_1px_2px_rgba(0,0,0,0.12)] border border-[#e3e2e6]">
              <FileUpload onFileUpload={handleFileUpload} />
            </div>
          </div>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-[#f9dedc] text-[#410e0b] p-4 rounded-xl mb-6 shadow-sm flex items-center gap-3 font-medium"
              >
                <svg className="w-5 h-5 text-[#b3261e]" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          <div className="flex flex-wrap justify-center gap-2 mb-8">
            <button
              onClick={() => setActiveTab('set-question-paper')}
              className={`font-medium py-2 px-6 rounded-full transition-all duration-200 text-sm ${
                activeTab === 'set-question-paper' 
                  ? 'bg-[#0b57d0] text-white shadow-sm' 
                  : 'bg-transparent text-[#444746] hover:bg-[#e3e2e6]'
              }`}
            >
              Paper Generator
            </button>
            <button
              onClick={() => setActiveTab('mcq-generator')}
              className={`font-medium py-2 px-6 rounded-full transition-all duration-200 text-sm ${
                activeTab === 'mcq-generator' 
                  ? 'bg-[#0b57d0] text-white shadow-sm' 
                  : 'bg-transparent text-[#444746] hover:bg-[#e3e2e6]'
              }`}
            >
              MCQ Generator
            </button>
            <button
              onClick={() => setActiveTab('course-analysis')}
              className={`font-medium py-2 px-6 rounded-full transition-all duration-200 text-sm flex items-center gap-2 ${
                activeTab === 'course-analysis' 
                  ? 'bg-[#0b57d0] text-white shadow-sm' 
                  : 'bg-transparent text-[#444746] hover:bg-[#e3e2e6]'
              }`}
            >
              <span className="w-2 h-2 bg-pink-500 rounded-full animate-pulse"></span>
              Course Analysis
            </button>
            <button
              onClick={() => setActiveTab('question-bank')}
              className={`font-medium py-2 px-6 rounded-full transition-all duration-200 text-sm flex items-center gap-2 ${
                activeTab === 'question-bank' 
                  ? 'bg-[#0b57d0] text-white shadow-sm' 
                  : 'bg-transparent text-[#444746] hover:bg-[#e3e2e6]'
              }`}
            >
              <Database size={16} />
              Question Bank
            </button>
            <button
              onClick={handleGetCourses}
              disabled={!file || loadingCourses}
              className={`font-medium py-2 px-6 rounded-full transition-all duration-200 text-sm disabled:opacity-30 ${
                activeTab === 'courses' 
                  ? 'bg-[#0b57d0] text-white shadow-sm' 
                  : 'bg-transparent text-[#444746] hover:bg-[#e3e2e6]'
              }`}
            >
              {loadingCourses ? 'Finding...' : 'NPTEL Matching'}
            </button>
          </div>
        </motion.div>
        
        <AnimatePresence mode="wait">
          {activeTab === 'courses' && (
            <motion.div
              key="courses"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Results courses={courses} />
            </motion.div>
          )}
          {activeTab === 'set-question-paper' && (
            <motion.div
              key="set-question-paper"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <SetQuestionPaper />
            </motion.div> 
          )}
          {activeTab === 'mcq-generator' && (
            <motion.div
              key="mcq-generator"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <MCQPaper />
            </motion.div> 
          )}
          {activeTab === 'course-analysis' && (
            <motion.div
              key="course-analysis"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <CourseAnalysis />
            </motion.div> 
          )}
          {activeTab === 'question-bank' && (
            <motion.div
              key="question-bank"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <QuestionBank />
            </motion.div> 
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default App;