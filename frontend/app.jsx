// App.jsx
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import ChatInterface from './components/ChatInterface';
import SearchInterface from './components/SearchInterface';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-white">
        <Navbar />
        <Routes>
          <Route path="/" element={<ChatInterface />} />
          <Route path="/search" element={<SearchInterface />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;