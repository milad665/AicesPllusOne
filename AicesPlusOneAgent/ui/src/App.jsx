import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SignedIn, SignedOut, SignInButton } from "@clerk/clerk-react";
import DashboardLayout from './layouts/DashboardLayout';
import DashboardView from './components/DashboardView';
import Settings from './components/Settings';
import AdminDashboard from './components/AdminDashboard';
import LandingPage from './components/LandingPage';
import Billing from './components/Billing';

function App() {
  return (
    <BrowserRouter>
      {/* Public / Landing Page */}
      <SignedOut>
        <LandingPage />
      </SignedOut>

      {/* Protected Routes */}
      <SignedIn>
        <Routes>
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<DashboardView />} />
            <Route path="settings" element={<Settings />} />
            <Route path="billing" element={<Billing />} />
            <Route path="admin" element={<AdminDashboard />} />
            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </SignedIn>
    </BrowserRouter>
  );
}

export default App;
