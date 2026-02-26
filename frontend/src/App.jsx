import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AutoModePage from './pages/AutoModePage';
import ManualModePage from './pages/ManualModePage';
import Navbar from './components/Navbar';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/auto" element={<AutoModePage />} />
          <Route path="/manual" element={<ManualModePage />} />
        </Routes>
      </main>
      <footer className="bg-white border-t mt-12">
        <div className="container mx-auto px-4 py-6 text-center text-gray-600">
          <p>历史数据仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
        </div>
      </footer>
    </div>
  );
}

export default App;