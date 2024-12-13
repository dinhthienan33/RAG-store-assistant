// components/SearchInterface.jsx
import React, { useState } from 'react';

function SearchInterface() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    try {
      const response = await fetch('http://localhost:5000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery }),
      });
      
      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="mb-8">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-purple-600"
            placeholder="Enter your search query..."
          />
          <button
            type="submit"
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700"
          >
            Search
          </button>
        </form>
      </div>

      {searchResults && (
        <div className="grid gap-4">
          {searchResults.map((result, idx) => (
            <div key={idx} className="bg-white p-4 rounded-lg shadow-md">
              {Object.entries(result).map(([key, value]) => (
                <div key={key} className="mb-2">
                  <span className="font-semibold text-purple-600">{key}: </span>
                  <span>{value}</span>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SearchInterface;