import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AssessmentPage from './AssessmentPage';

function AppRouter() {
    return (
        <Router basename="/app">
          <Routes>
            <Route path="/assessment" element={<AssessmentPage />} />
          </Routes>
        </Router>
      );
}

export default AppRouter;
