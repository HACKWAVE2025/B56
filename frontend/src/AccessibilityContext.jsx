import React, { createContext, useContext, useState } from 'react'; // <-- IMPORTED useContext

// 1. Create the Context object
export const AccessibilityContext = createContext();

// 2. Custom Hook to easily consume the context (THIS WAS MISSING)
export const useAccessibility = () => useContext(AccessibilityContext); // <-- NEW CUSTOM HOOK

// 3. Provider Component (Your original Component, now Step 3)
export const AccessibilityProvider = ({ children }) => {
  const [isDyslexicMode, setIsDyslexicMode] = useState(false);
  const [isHighContrast, setIsHighContrast] = useState(false);

  const toggleDyslexicMode = () => {
    setIsDyslexicMode(prev => !prev);
  };

  const toggleHighContrast = () => {
    setIsHighContrast(prev => !prev);
  };

  const value = {
    isDyslexicMode,
    toggleDyslexicMode,
    isHighContrast,
    toggleHighContrast,
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  );
};