import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './auth/Login';
import Dashboard from './components/Dashboard';

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // TODO: check Firebase auth state
  }, []);

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  return (
    <Routes>
      <Route path="/" element={<Dashboard user={user} />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;