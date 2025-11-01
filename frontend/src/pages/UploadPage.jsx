import React, { useState } from 'react';
import { useAccessibility } from '../AccessibilityContext'; // <-- NEW IMPORT

// --- API CONSTANTS ---
const API_BASE_URL = 'http://127.0.0.1:5000';
const UPLOAD_API_URL = `${API_BASE_URL}/api/upload`;
const RESULT_API_URL = `${API_BASE_URL}/api/result`;
// --------------------

// --- NEW Component: Settings Panel ---
const SettingsPanel = () => {
  // Use the context to get state and togglers
  const { 
    isDyslexicMode, 
    toggleDyslexicMode, 
    isHighContrast, 
    toggleHighContrast 
  } = useAccessibility();

  const Checkbox = ({ checked, onChange, label }) => (
    <div className="flex items-center space-x-2">
      <input
        type="checkbox"
        id={label}
        checked={checked}
        onChange={onChange}
        className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
      />
      <label htmlFor={label} className="text-sm font-medium text-gray-700">
        {label}
      </label>
    </div>
  );

  return (
    <div className="p-4 bg-indigo-50 border-t border-b border-indigo-200 shadow-inner rounded-b-lg mb-6">
      <h3 className="text-lg font-semibold text-indigo-800 mb-3 border-b pb-2">Accessibility Settings</h3>
      <div className="flex flex-wrap gap-6">
        <Checkbox 
          checked={isDyslexicMode} 
          onChange={toggleDyslexicMode} 
          label="Dyslexia Friendly Font" 
        />
        <Checkbox 
          checked={isHighContrast} 
          onChange={toggleHighContrast} 
          label="High Contrast Theme" 
        />
      </div>
    </div>
  );
};
// -------------------------------------


function UploadPage() {
  // --- USE ACCESSIBILITY CONTEXT ---
  const { isDyslexicMode, isHighContrast } = useAccessibility(); 
  // ---------------------------------

  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  
  const [simplifiedHtml, setSimplifiedHtml] = useState(null);
  const [audioPath, setAudioPath] = useState(null);

  const fetchSimplifiedContent = async (filename) => {
    try {
      const response = await fetch(`${RESULT_API_URL}/${filename}`);
      if (!response.ok) throw new Error("Failed to fetch simplified file.");
      
      const htmlText = await response.text();
      setSimplifiedHtml(htmlText);

    } catch (error) {
      console.error("Fetch Content Error:", error); 
      setStatus(`Error fetching content: ${error.message}`);
      setSimplifiedHtml("Could not load simplified content.");
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && (selectedFile.type === 'application/pdf' || 
                        selectedFile.name.endsWith('.docx'))) {
      setFile(selectedFile);
      setStatus(`File selected: ${selectedFile.name}`);
      setSimplifiedHtml(null);
      setAudioPath(null);
    } else {
      setFile(null);
      setStatus('Please select a PDF or DOCX file.');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus('Please select a file first.');
      return;
    }

    setLoading(true);
    setStatus('Uploading and processing...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(UPLOAD_API_URL, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorData = {};
        try { errorData = await response.json(); } catch {}
        setStatus(`Conversion Failed: ${errorData.message || 'Server returned an error.'}`);
        setLoading(false);
        return;
      }
      
      const data = await response.json(); 

      if (data.status === 'COMPLETED') { 
        setStatus(`Success! Task ID: ${data.task_id}. Results are ready.`);
        
        if (data.simplified_file) {
          await fetchSimplifiedContent(data.simplified_file);
        }
        if (data.audio_file) {
          setAudioPath(`${RESULT_API_URL}/${data.audio_file}`);
        } else {
          setStatus(prev => prev + " (Note: TTS audio generation failed.)");
        }

      } else {
        setStatus(`Conversion Failed: ${data.message || 'Internal logic error.'}`);
      }

    } catch (error) {
      console.error('Upload Error (Caught - Network/CORS/JSON Fail):', error);
      setStatus(`Network or connection error. Is the Flask server running? Check browser console for CORS errors.`);
    } finally {
      setLoading(false);
    }
  };

  // Dynamically compute the class names for the results container
  const resultsClasses = `space-y-8 p-4 border rounded-lg transition-colors duration-300 ${
    isHighContrast ? 'theme-high-contrast' : 'bg-green-50'
  }`;
  
  // Dynamically compute the class names for the content itself
  const contentClasses = `simplified-content space-y-4 ${
    isDyslexicMode ? 'font-dyslexic' : ''
  }`;


  return (
    <div className="space-y-6">
      {!simplifiedHtml ? (
        // --- UPLOADER VIEW ---
        <>
          <div className="border-2 border-dashed border-indigo-300 rounded-lg p-10 text-center cursor-pointer hover:border-indigo-500 transition duration-150">
            <input 
              type="file" 
              onChange={handleFileChange} 
              accept=".pdf,.docx"
              className="hidden" 
              id="file-upload"
            />
            <label htmlFor="file-upload" className="block text-gray-600 font-medium">
              {file ? file.name : 'Drag & Drop your PDF/DOCX here, or click to browse'}
            </label>
            <p className="mt-1 text-sm text-gray-400">Max size 50MB</p>
          </div>

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className={`w-full py-3 px-4 rounded-md font-semibold text-white transition duration-150 
              ${!file || loading 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-indigo-600 hover:bg-indigo-700'
              }`}
          >
            {loading ? 'Processing...' : 'Generate Accessible Version'}
          </button>
        </>
      ) : (
        // --- RESULTS VIEW ---
        <div className={resultsClasses}>
          
          <SettingsPanel /> {/* <-- NEW SETTINGS PANEL RENDERED HERE */}

          <h2 className="text-2xl font-bold text-green-700">✅ Conversion Complete!</h2>
          
          {/* Audio Player Section */}
          <div className="border p-4 bg-white rounded-md shadow">
            <h3 className="text-xl font-semibold mb-2">🔊 TTS Audio Playback</h3>
            {audioPath ? (
              <audio controls src={audioPath} className="w-full">
                Your browser does not support the audio element.
              </audio>
            ) : (
              <p className="text-red-500">Audio file path missing or failed generation.</p>
            )}
            {audioPath && <a href={audioPath} download className="mt-2 inline-block text-indigo-600 hover:text-indigo-800 text-sm">(Download MP3)</a>}
          </div>

          {/* Simplified Text Section - Dynamic Styles Applied */}
          <div className="border p-4 bg-white rounded-md shadow">
            <h3 className="text-xl font-semibold mb-2">📖 Simplified Content</h3>
            <div 
              className={contentClasses} // <-- DYNAMIC CLASS APPLIED HERE
              dangerouslySetInnerHTML={{ __html: simplifiedHtml }}
            />
          </div>

          <button
            onClick={() => { setSimplifiedHtml(null); setFile(null); setStatus(''); setAudioPath(null); }}
            className="w-full py-3 px-4 rounded-md font-semibold text-white bg-blue-600 hover:bg-blue-700 transition duration-150"
          >
            Start New Conversion
          </button>
        </div>
      )}

      {/* Status Bar (Always Visible) */}
      {status && (
        <p className={`text-sm p-3 rounded-md text-center ${status.includes('Success') || status.includes('ready') ? 'bg-green-100 text-green-700' : status.includes('Failed') || status.includes('error') ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
          {status}
        </p>
      )}
    </div>
  );
}

export default UploadPage;