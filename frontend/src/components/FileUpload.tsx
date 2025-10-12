import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaCloudUploadAlt, FaCheckCircle } from 'react-icons/fa';
import { motion, AnimatePresence } from 'framer-motion';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success'>('idle');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setUploadStatus('uploading');
      onFileUpload(acceptedFiles[0]);
      setTimeout(() => setUploadStatus('success'), 1000); // Simulating upload time
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false,
  });

  return (
    <div className="mt-8 w-full">
      <div
        {...getRootProps()}
        className={`max-w-2xl mx-auto border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition duration-300 ease-in-out ${
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-500'
        }`}
      >
        <input {...getInputProps()} />
        <AnimatePresence mode="wait">
          {uploadStatus === 'idle' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <FaCloudUploadAlt className="text-5xl text-blue-500 mx-auto mb-4" />
              <p className="text-gray-600">
                {isDragActive
                  ? 'Drop the PDF here'
                  : "Drag and drop a PDF file here, or click to select one"}
              </p>
            </motion.div>
          )}
          {uploadStatus === 'uploading' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-blue-600">Uploading...</p>
            </motion.div>
          )}
          {uploadStatus === 'success' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <FaCheckCircle className="text-5xl text-green-500 mx-auto mb-4" />
              <p className="text-green-600">File uploaded successfully!</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      {acceptedFiles.length > 0 && uploadStatus === 'success' && (
        <div className="mt-4 text-center">
          <p className="text-green-600">
            File uploaded: {acceptedFiles[0].name}
          </p>
        </div>
      )}
    </div>
  );
};

export default FileUpload;