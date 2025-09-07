// frontend/src/components/Dashboard.jsx
import React from 'react';
import AnalysisPanel from './AnalysisPanel';
import HistoryPanel from './HistoryPanel';

export default function Dashboard({ user }) {
  return (
    <div className="dashboard">
      <header>
        <h1>PathoScope</h1>
        <span>Welcome, {user.email}</span>
      </header>
      <main>
        <AnalysisPanel />
        <HistoryPanel />
      </main>
    </div>
  );
}