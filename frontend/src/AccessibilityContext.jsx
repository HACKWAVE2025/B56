import React, { createContext, useContext, useState } from 'react'; // <-- IMPORTED useContext

// 1. Create the Context object
export const AccessibilityContext = createContext();

// 2. Custom Hook to easily consume the context (THIS WAS MISSING)
export const useAccessibility = () => useContext(AccessibilityContext); // <-- NEW CUSTOM HOOK

// 3. Provider Component (Your original Component, now Step 3)
export const AccessibilityProvider = ({ children }) => {
  const [isDyslexicMode, setIsDyslexicMode] = useState(false);
  const [isColorInverted, setIsColorInverted] = useState(false); // New state for color inversion

  const toggleDyslexicMode = () => {
    setIsDyslexicMode(prev => !prev);
  };

  const toggleColorInversion = () => { // New function to toggle color inversion
    setIsColorInverted(prev => !prev);
  };

  const value = {
    isDyslexicMode,
    toggleDyslexicMode,
    isColorInverted, // Expose new state
    toggleColorInversion, // Expose new function
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  );
};