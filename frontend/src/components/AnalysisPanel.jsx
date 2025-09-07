// frontend/src/components/AnalysisPanel.jsx
import React, { useState } from 'react';
import axios from 'axios';
// Add import for marked
import { marked } from 'marked';
import './styles.css';

export default function AnalysisPanel() {
  const [disease, setDisease] = useState('');
  const [file, setFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [result, setResult] = useState(null);

  const startAnalysis = async () => {
    const form = new FormData();
    form.append('disease_name', disease);
    if (file) form.append('csv_file', file);
    const { data } = await axios.post('/api/analyze', form);
    setJobId(data.job_id);
  };

  const pollResult = async () => {
    if (!jobId) return;
    const res = await axios.get(`/api/results/${jobId}`);
    if (res.status === 202) return;
    setResult(res.data);
  };

  return (
    <div className="analysis-panel">
      <input
        type="text"
        placeholder="Disease name"
        value={disease}
        onChange={e => setDisease(e.target.value)}
      />
      <input
        type="file"
        accept=".csv"
        onChange={e => setFile(e.target.files[0])}
      />
      <button onClick={startAnalysis}>Analyze</button>
      {jobId && <button onClick={pollResult}>Get Result</button>}
      {result && (
        <div className="results">
          <h3>Explanation</h3>
          <div
            className="ai-explanation-box"
            dangerouslySetInnerHTML={{ __html: marked.parse((result.explanation || '').replace(/\*\*/g, '').replace(/\*+/g, '')) }}
          />
        </div>
      )}
    </div>
  );
}