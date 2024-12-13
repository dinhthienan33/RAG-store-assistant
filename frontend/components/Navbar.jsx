// components/Navbar.jsx
import React from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-xl font-bold text-purple-600">Negotio</h1>
            </div>
            <div className="ml-6 flex space-x-8">
              <Link to="/" className="inline-flex items-center px-1 pt-1 text-gray-900">
                Tư vấn
              </Link>
              <Link to="/search" className="inline-flex items-center px-1 pt-1 text-gray-900">
                Tìm kiếm
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;