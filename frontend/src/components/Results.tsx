import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaClock, FaChalkboardTeacher, FaExternalLinkAlt, FaChartBar, FaSearch } from 'react-icons/fa';
import { Course } from '../types';

interface ResultsProps {
  courses: Course[];
}

const Results: React.FC<ResultsProps> = ({ courses }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const filteredCourses = courses.filter(course =>
    course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    course.instructors.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mt-12 px-4 sm:px-6 lg:px-8"
    >
      <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
        Recommended Courses for Your Syllabus
      </h2>
      <div className="mb-6 max-w-md mx-auto">
        <div className="relative">
          <input
            type="text"
            placeholder="Search courses or instructors..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onFocus={() => setIsSearchFocused(true)}
            onBlur={() => setIsSearchFocused(false)}
            className={`w-full px-4 py-2 rounded-full border-2 ${
              isSearchFocused ? 'border-teal-500 ring-2 ring-teal-200' : 'border-teal-300'
            } outline-none transition-all duration-300 pr-10 bg-white text-gray-800 placeholder-gray-500`}
          />
          <FaSearch className="absolute right-3 top-1/2 transform -translate-y-1/2 text-teal-500" />
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 w-full">
        {filteredCourses.map((course) => (
          <motion.div
            key={course.id}
            layoutId={course.id}
            onClick={() => toggleExpand(course.id)}
            whileHover={{ scale: 1.03 }}
            className="relative bg-gradient-to-br from-white to-teal-50 rounded-2xl shadow-lg overflow-hidden cursor-pointer transform transition-all duration-300 hover:shadow-2xl border-2 border-teal-300 hover:border-teal-500"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-teal-100 to-blue-50 opacity-80"></div>
            <div className="relative p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-3 line-clamp-2">{course.title}</h3>
              <div className="flex items-center text-gray-600 mb-2">
                <FaClock className="mr-2 text-teal-500" />
                <span>{course.duration}</span>
              </div>
              <div className="flex items-center text-gray-600 mb-4">
                <FaChalkboardTeacher className="mr-2 text-teal-500" />
                <span className="line-clamp-1">{course.instructors}</span>
              </div>
              <div className="relative pt-1">
                <div className="flex mb-2 items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-teal-700 bg-teal-300">
                      Relevance
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-semibold inline-block text-teal-600">
                      {(course.similarity * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-teal-200">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${course.similarity * 100}%` }}
                    transition={{ duration: 0.5, ease: "easeInOut" }}
                    className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-teal-500"
                  ></motion.div>
                </div>
              </div>
            </div>
            <AnimatePresence>
              {expandedId === course.id && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className="relative px-6 pb-6"
                >
                  <p className="text-gray-600 mb-4">
                    This course is {(course.similarity * 100).toFixed(0)}% relevant to your syllabus.
                  </p>
                  <a
                    href={course.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-teal-600 hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 transition-colors duration-200"
                  >
                    View Course <FaExternalLinkAlt className="ml-2" />
                  </a>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
      {filteredCourses.length === 0 && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center text-gray-600 mt-8"
        >
          No courses found matching your search. Try adjusting your search terms.
        </motion.p>
      )}
    </motion.div>
  );
};

export default Results;