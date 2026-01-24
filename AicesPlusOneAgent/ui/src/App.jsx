import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SignedIn, SignedOut, SignInButton } from "@clerk/clerk-react";
import DashboardLayout from './layouts/DashboardLayout';
import DashboardView from './components/DashboardView';
import Settings from './components/Settings';
import AdminDashboard from './components/AdminDashboard';
import Billing from './components/Billing';

function App() {
  return (
    <BrowserRouter>
      {/* Public / Auth Wall */}
      <SignedOut>
        <div className="flex h-screen items-center justify-center bg-gray-900 text-white">
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold mb-8">Aices Plus One</h1>
            <p className="text-gray-400 mb-8">Enterprise Architecture Observability Platform</p>
            <SignInButton mode="modal">
              <button className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg text-lg font-medium shadow-lg hover:shadow-blue-500/20 transition-all">
                Sign In to Dashboard
              </button>
            </SignInButton>
          </div>
        </div>
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
