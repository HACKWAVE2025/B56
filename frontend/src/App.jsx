import React from 'react';
import UploadPage from './pages/UploadPage';
import { AccessibilityProvider } from './AccessibilityContext'; // <-- NEW IMPORT
import './index.css';

function App() {
  return (
    // Wrap the entire application in the provider
    <AccessibilityProvider> 
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-full max-w-2xl p-8 bg-white shadow-xl rounded-lg">
          <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">
            Accessibility Learning Hub
          </h1>
          <UploadPage />
        </div>
      </div>
    </AccessibilityProvider>
  );
}

export default App;