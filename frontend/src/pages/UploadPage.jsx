import React, { useState } from 'react';
import { useAccessibility } from '../AccessibilityContext'; 
// import { SettingsPanel } from '../components/SettingsPanel'; // REMOVED: No longer needed as it's defined below

// --- API CONSTANTS ---
const API_BASE_URL = 'http://127.0.0.1:5000';
const UPLOAD_API_URL = `${API_BASE_URL}/api/upload`;
const RESULT_API_URL = `${API_BASE_URL}/api/result`;
// --------------------

// NOTE: Since the SettingsPanel component code might conflict 
// with the file structure, defining it here for a single-file solution.
const SettingsPanel = () => {
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


function UploadPage() {
    const { isDyslexicMode, isHighContrast } = useAccessibility(); 
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState('');
    const [loading, setLoading] = useState(false);
    
    const [simplifiedHtml, setSimplifiedHtml] = useState(null);
    const [audioPath, setAudioPath] = useState(null);
    const [accessibilityReport, setAccessibilityReport] = useState(null); // <-- NEW STATE

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
            setAccessibilityReport(null); // Reset report
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
                }
                
                // NEW: Parse and store the report JSON
                if (data.report) {
                    try {
                        setAccessibilityReport(JSON.parse(data.report));
                    } catch (e) {
                        console.error("Failed to parse report JSON:", e);
                        setStatus(prev => prev + " (Report data is corrupt.)");
                    }
                } else {
                    setStatus(prev => prev + " (Report generation failed.)");
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

    // Helper component to display the report
    const ReportDisplay = ({ report }) => {
        if (!report) return null;

        const isPass = report.summary_score && report.summary_score.startsWith('PASS');
        const scoreColor = isPass ? 'bg-green-100 text-green-800 border-green-300' : 'bg-yellow-100 text-yellow-800 border-yellow-300';

        const formatValue = (key, value) => {
            if (key.includes("grade")) return value;
            if (key.includes("status")) return value;
            // The logic here seems to force string formatting; removed the float conversion for safety.
            return value;
        };

        return (
            <div className className={`p-4 mt-6 border rounded-lg shadow-md ${scoreColor}`}>
                <h3 className="text-xl font-bold mb-3">Accessibility Report</h3>
                
                <div className className="mb-4 p-2 border-b border-opacity-50">
                    <span className="font-semibold">Overall Score:</span> 
                    <span className={`ml-2 font-extrabold ${isPass ? 'text-green-600' : 'text-yellow-600'}`}>
                        {report.summary_score}
                    </span>
                </div>

                <div className="space-y-3">
                    <h4 className="font-semibold text-lg">Readability Metrics</h4>
                    {Object.entries(report.readability_metrics).map(([key, value]) => (
                        <div key={key} className="flex justify-between text-sm">
                            <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span>
                            <span>{value}</span>
                        </div>
                    ))}

                    <h4 className="font-semibold text-lg pt-2 border-t mt-2">Structure Analysis</h4>
                    {Object.entries(report.structure_analysis).map(([key, value]) => (
                         // Skip notes
                        (key !== 'note' && key !== 'alt_missing_count') && (
                            <div key={key} className="flex justify-between text-sm">
                                <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span>
                                <span>{value}</span>
                            </div>
                        )
                    ))}
                </div>
            </div>
        );
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
                    
                    <SettingsPanel />

                    <h2 className="text-2xl font-bold text-green-700">✅ Conversion Complete!</h2>
                    
                    {accessibilityReport && <ReportDisplay report={accessibilityReport} />} {/* <-- NEW REPORT DISPLAY */}
                    
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
                            className={contentClasses} 
                            dangerouslySetInnerHTML={{ __html: simplifiedHtml }}
                        />
                    </div>

                    <button
                        onClick={() => { setSimplifiedHtml(null); setFile(null); setStatus(''); setAudioPath(null); setAccessibilityReport(null); }}
                        className="w-full py-3 px-4 rounded-md font-semibold text-white bg-blue-600 hover:bg-blue-700 transition duration-150"
                    >
                        Start New Conversion
                    </button>
                </div>
            )}

            // ... Status Bar (Always Visible) ...
            {status && (
                <p className={`text-sm p-3 rounded-md text-center ${status.includes('Success') || status.includes('ready') ? 'bg-green-100 text-green-700' : status.includes('Failed') || status.includes('error') ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
                    {status}
                </p>
            )}
        </div>
    );
}

export default UploadPage;
