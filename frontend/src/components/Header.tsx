import React from 'react';
import { FaGraduationCap } from 'react-icons/fa';

const Header: React.FC = () => {
  return (
    <header className="sticky top-0 bg-white shadow-md z-10">
      <div className="container mx-auto px-4 py-6 flex items-center">
        <FaGraduationCap className="text-4xl text-blue-500 mr-4" />
        <h1 className="text-2xl font-bold text-gray-800">Knowledge Hub</h1>
      </div>
    </header>
  );
};

export default Header;
