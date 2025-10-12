import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Book, ExternalLink, ChevronDown, ChevronUp, Search } from 'lucide-react';

interface Resource {
  title: string;
  link: string;
  snippet: string;
  relevance_score: number;
}

interface ResourcesProps {
  resources: Resource[];

}

const Resources: React.FC<ResourcesProps> = ({ resources }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
    
  };

  const filteredResources = resources.filter(resource =>
    resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    resource.snippet.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mt-12 px-4 sm:px-6 lg:px-8"
    >
      <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
        Learning Resources for Your Syllabus
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 w-full">
        {filteredResources.map((resource, index) => (
          <motion.div
            key={index}
            layoutId={`resource-${index}`}
            onClick={() => toggleExpand(`resource-${index}`)}
            whileHover={{ scale: 1.03 }}
            className="relative bg-gradient-to-br from-white to-purple-50 rounded-2xl shadow-lg overflow-hidden cursor-pointer transform transition-all duration-300 hover:shadow-2xl border-2 border-purple-300 hover:border-purple-500"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-purple-100 to-blue-50 opacity-80"></div>
            <div className="relative p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-3 line-clamp-2">{resource.title}</h3>
              <div className="flex items-center text-gray-600 mb-2">
                <Book className="mr-2 text-purple-500" size={18} />
                <span className="line-clamp-1">Learning Resource</span>
              </div>
              <div className="flex items-center text-gray-600 mb-4">
                <Search className="mr-2 text-purple-500" size={18} />
                <span className="line-clamp-2">{resource.snippet}</span>
              </div>
              <div className="relative pt-1">
                <div className="flex mb-2 items-center justify-between">
                  <div>
                    <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-purple-700 bg-purple-300">
                      Relevance
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-semibold inline-block text-purple-600">
                      {isNaN(resource.relevance_score) ? "N/A" : `${(resource.relevance_score * 100).toFixed(0)}%`}
                    </span>
                  </div>
                </div>
                <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-purple-200">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${isNaN(resource.relevance_score) ? 0 : resource.relevance_score * 100}%` }}
                    transition={{ duration: 0.5, ease: "easeInOut" }}
                    className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-purple-500"
                  ></motion.div>
                </div>
              </div>
            </div>
            <AnimatePresence>
              {expandedId === `resource-${index}` && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className="relative px-6 pb-6"
                >
                  <p className="text-gray-600 mb-4">
                    This resource is {isNaN(resource.relevance_score) ? "not relevant" : `${(resource.relevance_score * 100).toFixed(0)}% relevant`} to your syllabus.
                  </p>
                  <a
                    href={resource.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors duration-200"
                    onClick={(e) => e.stopPropagation()}
                  >
                    View Resource <ExternalLink className="ml-2" size={16} />
                  </a>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
      {filteredResources.length === 0 && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center text-gray-600 mt-8"
        >
          No resources found matching your search. Try adjusting your search terms.
        </motion.p>
      )}
    </motion.div>
  );
};

export default Resources;

