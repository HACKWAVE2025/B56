import React from 'react';
import UploadPage from './pages/UploadPage';
import { AccessibilityProvider, useAccessibility } from './AccessibilityContext';
import './index.css';

function AppContent() {
  const { isDyslexicMode, isColorInverted } = useAccessibility();

  // Build the className string based on the accessibility settings
  const appClasses = [
    "min-h-screen",
    "bg-gray-50",
    "flex",
    "items-center",
    "justify-center",
    isDyslexicMode ? "font-dyslexic" : "",
    isColorInverted ? "theme-color-inverted" : "",
  ].filter(Boolean).join(" ");

  return (
    <div className={appClasses}>
      <div className="w-full max-w-2xl p-8 bg-white shadow-xl rounded-lg">
        <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">
          Accessibility Learning Hub
        </h1>
        <UploadPage />
      </div>
    </div>
  );
}


function App() {
  return (
    <AccessibilityProvider> 
      <AppContent />
    </AccessibilityProvider>
  );
}

export default App;