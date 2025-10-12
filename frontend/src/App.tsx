import React, { useState } from 'react';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import Results from './components/Results';
import Resources from './components/Resources';
import { motion, AnimatePresence } from 'framer-motion';
import { uploadPDF, getCourses, getResources } from './services/api';
import { Resource } from './types';
import SetQuestionPaper from './components/SetQuestionPaper';

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [courses, setCourses] = useState<any[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loadingCourses, setLoadingCourses] = useState<boolean>(false);
  const [loadingResources, setLoadingResources] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'courses' | 'resources' | 'set-question-paper'>('courses');

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

  const handleGetResources = async () => {
    setLoadingResources(true);
    setError(null);
    try {
      const resourcesData = await getResources();
      setResources(resourcesData);
      setActiveTab('resources');
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error || 'Unexpected error occurred. Please try again.';
      setError(errorMessage);
      console.error(err);
    } finally {
      setLoadingResources(false);
    }
  };

  const isLoading = loadingCourses || loadingResources;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-100">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <FileUpload onFileUpload={handleFileUpload} />
          <AnimatePresence>
            {error && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="text-red-500 text-center mt-4"
              >
                {error}
              </motion.p>
            )}
          </AnimatePresence>
          <div className="flex justify-center space-x-4 mt-8">
            <button
              onClick={handleGetCourses}
              disabled={!file || isLoading}
              className={`bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300 ease-in-out transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed ${
                loadingCourses ? 'animate-pulse' : ''
              }`}
            >
              {loadingCourses ? 'Loading Courses...' : 'Get Courses'}
            </button>
            <button
              onClick={handleGetResources}
              disabled={!file || isLoading}
              className={`bg-purple-500 hover:bg-purple-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300 ease-in-out transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed ${
                loadingResources ? 'animate-pulse' : ''
              }`}
            >
              {loadingResources ? 'Loading Resources...' : 'Get Learning Resources'}
            </button>
            <button
              onClick={() => setActiveTab('set-question-paper')}
              disabled={!file || isLoading}
              className={`bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300 ease-in-out transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed ${
                activeTab === 'set-question-paper' ? 'ring-2 ring-green-300' : ''
              }`}
            >
              Set Question Paper
            </button>
          </div>
        </motion.div>
        <AnimatePresence mode="wait">
          {activeTab === 'courses' && courses.length > 0 && (
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
          {activeTab === 'resources' && resources.length > 0 && (
            <motion.div
              key="resources"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Resources resources={resources} />
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
        </AnimatePresence>
      </main>
    </div>
  );
};

export default App;