// frontend/src/components/HistoryPanel.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function HistoryPanel() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    axios.get('/api/history').then(res => setHistory(res.data));
  }, []);

  const deleteItem = async idx => {
    await axios.delete(`/api/history/${idx}`);
    setHistory(history.filter((_, i) => i !== idx));
  };

  return (
    <div className="history-panel">
      <h2>Search History</h2>
      {history.length ? (
        <ul>
          {history.map((h, i) => (
            <li key={i}>
              <strong>{h.disease || '—'}</strong>
              <button onClick={() => deleteItem(i)}>Delete</button>
            </li>
          ))}
        </ul>
      ) : (
        <p>No history yet.</p>
      )}
    </div>
  );
}