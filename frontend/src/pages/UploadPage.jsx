import React, { useState } from 'react';
import { useAccessibility } from '../AccessibilityContext'; 
import { ChevronDown, FileText, Loader, Zap, Download } from 'lucide-react'; 

// --- API CONSTANTS ---
const API_BASE_URL = 'http://127.0.0.1:5000';
const UPLOAD_API_URL = `${API_BASE_URL}/api/upload`;
const RESULT_API_URL = `${API_BASE_URL}/api/result`;
const DOWNLOAD_EPUB_URL = `${API_BASE_URL}/api/download/epub`; 
const DOWNLOAD_PDF_URL = `${API_BASE_URL}/api/download/pdf`; // NEW CONSTANT
// --------------------

// NOTE: SettingsPanel component defined locally for single-file operation
const SettingsPanel = () => {
    const { 
        isDyslexicMode, 
        toggleDyslexicMode, 
        isHighContrast, 
        toggleHighContrast 
    } = useAccessibility();

    const Checkbox = ({ checked, onChange, label }) => (
        <div className="flex items-center space-x-2 cursor-pointer">
            <input
                type="checkbox"
                id={label.replace(/\s/g, '-') + '-checkbox'}
                checked={checked}
                onChange={onChange}
                className="h-4 w-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
            />
            <label htmlFor={label.replace(/\s/g, '-') + '-checkbox'} className="text-sm font-medium text-gray-700">
                {label}
            </label>
        </div>
    );

    return (
        <div className="p-4 bg-gray-50 border-t border-b border-gray-200 shadow-inner rounded-b-lg mb-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-3 border-b pb-2 flex items-center gap-2">
                <Zap className="w-4 h-4 text-purple-600" /> Accessibility Settings
            </h3>
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

// Helper component to display the report
const ReportDisplay = ({ report }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    if (!report) return null;

    const isPass = report.summary_score && report.summary_score.startsWith('PASS');
    const scoreColor = isPass ? 'bg-green-600 text-white' : 'bg-yellow-500 text-gray-900';
    const bodyColor = isPass ? 'border-green-300' : 'border-yellow-300';
    const detailColor = isPass ? 'bg-green-50' : 'bg-yellow-50';

    return (
        <div className={`p-4 mt-6 border rounded-xl shadow-lg transition-all duration-300 ${bodyColor}`}>
            <button 
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex justify-between items-center text-left py-2 font-bold text-lg"
            >
                <span className={`px-3 py-1 rounded-full text-sm ${scoreColor}`}>
                    {report.summary_score}
                </span>
                <ChevronDown className={`w-5 h-5 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} />
            </button>
            
            {isExpanded && (
                <div className={`mt-3 p-4 rounded-lg ${detailColor} space-y-4`}>
                    <h4 className="font-semibold text-lg border-b pb-2">Readability Metrics</h4>
                    {Object.entries(report.readability_metrics).map(([key, value]) => (
                        <div key={key} className="flex justify-between text-sm">
                            <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span>
                            <span className="font-mono">{value}</span>
                        </div>
                    ))}

                    <h4 className="font-semibold text-lg pt-2 border-t mt-2">Structure Analysis</h4>
                    {Object.entries(report.structure_analysis).map(([key, value]) => (
                         // Skip notes and intermediate counters
                        (key !== 'note' && key !== 'alt_missing_count') && (
                            <div key={key} className="flex justify-between text-sm">
                                <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span>
                                <span className={value === 'Missing' ? 'text-red-500 font-bold' : 'text-gray-700'}>{value}</span>
                            </div>
                        )
                    ))}
                </div>
            )}
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
    const [accessibilityReport, setAccessibilityReport] = useState(null);
    const [epubPath, setEpubPath] = useState(null); 
    const [pdfPath, setPdfPath] = useState(null); // PDF Path State

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
            setAccessibilityReport(null);
            setEpubPath(null); 
            setPdfPath(null); // Reset PDF Path
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
                if (data.epub_file) {
                    setEpubPath(`${DOWNLOAD_EPUB_URL}/${data.epub_file}`);
                }
                if (data.pdf_file) { // Path assigned for PDF download
                    setPdfPath(`${DOWNLOAD_PDF_URL}/${data.pdf_file}`);
                }
                
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

    // Dynamically compute the class names for the results container
    const resultsClasses = `space-y-8 p-6 transition-colors duration-300 border-t-8 border-purple-600 rounded-2xl shadow-2xl ${
        isHighContrast ? 'theme-high-contrast' : 'bg-white'
    }`;
    
    // Dynamically compute the class names for the content itself
    const contentClasses = `simplified-content space-y-4 p-4 border rounded-lg bg-gray-50 shadow-inner ${
        isDyslexicMode ? 'font-dyslexic' : 'font-sans'
    }`;


    return (
        <div className="space-y-6">
            {!simplifiedHtml ? (
                // --- UPLOADER VIEW (Colorful and unique design) ---
                <>
                    <div className="bg-indigo-50 p-10 border-4 border-dashed border-indigo-300 rounded-2xl text-center cursor-pointer hover:border-purple-500 transition duration-300 transform hover:scale-[1.01] shadow-xl">
                        <FileText className="w-12 h-12 text-indigo-500 mx-auto mb-4" />
                        <input 
                            type="file" 
                            onChange={handleFileChange} 
                            accept=".pdf,.docx"
                            className="hidden" 
                            id="file-upload"
                        />
                        <label htmlFor="file-upload" className="block text-xl font-bold text-gray-700 cursor-pointer">
                            {file ? file.name : 'Choose or Drag & Drop your Educational Material'}
                        </label>
                        <p className="mt-1 text-sm text-indigo-400">PDF, DOCX, or URL (max 50MB)</p>
                    </div>

                    <button
                        onClick={handleUpload}
                        disabled={!file || loading}
                        className={`w-full py-4 px-6 rounded-xl font-extrabold text-white text-lg shadow-lg transition duration-200 transform hover:scale-[1.005] 
                          ${!file || loading 
                            ? 'bg-gray-400 cursor-not-allowed shadow-none' 
                            : 'bg-purple-600 hover:bg-purple-700 focus:ring-4 focus:ring-purple-300'
                          }`}
                    >
                        {loading ? (
                            <span className="flex items-center justify-center"><Loader className="w-5 h-5 mr-2 animate-spin" /> Processing...</span>
                        ) : (
                            'Generate Accessible Version'
                        )}
                    </button>
                </>
            ) : (
                // --- RESULTS VIEW (Clean and organized) ---
                <div className={resultsClasses}>
                    
                    <SettingsPanel />

                    <h2 className="text-2xl font-bold text-purple-700 border-b pb-2">✅ Conversion Complete!</h2>
                    
                    {accessibilityReport && <ReportDisplay report={accessibilityReport} />}
                    
                    {/* Audio Controls - RESTORED VISIBLE AUDIO TAG */}
                    {audioPath && (
                        <div className="p-4 border rounded-lg bg-white shadow-md">
                            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2 text-gray-700">
                                🔊 Audio Playback
                            </h3>
                            <audio controls src={audioPath} className="w-full rounded-md shadow-inner">
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                    )}
                    
                    {/* DOWNLOAD BUTTONS */}
                    <div className="flex flex-col sm:flex-row gap-4 p-4 border rounded-xl bg-purple-50 shadow-inner">
                        {/* EPUB Download */}
                        {epubPath && (
                            <a href={epubPath} download className="flex-1">
                                <button className="w-full py-3 px-4 flex items-center justify-center gap-2 rounded-xl font-semibold text-white bg-indigo-500 hover:bg-indigo-600 transition duration-150 shadow-md">
                                    <Download className="w-5 h-5" /> Download EPUB
                                </button>
                            </a>
                        )}
                         {/* PDF Download (NEW) */}
                        {pdfPath && (
                            <a href={pdfPath} download className="flex-1">
                                <button className="w-full py-3 px-4 flex items-center justify-center gap-2 rounded-xl font-semibold text-white bg-red-600 hover:bg-red-700 transition duration-150 shadow-md">
                                    <Download className="w-5 h-5" /> Download PDF
                                </button>
                            </a>
                        )}
                        {/* Audio Download */}
                        {audioPath && (
                            <a href={audioPath} download className="flex-1">
                                <button className="w-full py-3 px-4 flex items-center justify-center gap-2 rounded-xl font-semibold text-indigo-700 border border-indigo-500 bg-white hover:bg-indigo-50 transition duration-150 shadow-md">
                                    <span role="img" aria-label="Audio download">🎧</span> Download Audio (MP3)
                                </button>
                            </a>
                        )}
                    </div>
                    
                    {/* Simplified Content Viewer */}
                    <div className="p-0">
                        <h3 className="text-lg font-semibold mb-2 flex items-center gap-2 text-gray-700">
                            <span role="img" aria-label="Book emoji">📖</span> Simplified Content Viewer
                        </h3>
                        
                        <div className={contentClasses}>
                            <div 
                                className="text-gray-800"
                                dangerouslySetInnerHTML={{ __html: simplifiedHtml }}
                            />
                        </div>
                    </div>

                    <button
                        onClick={() => { setSimplifiedHtml(null); setFile(null); setStatus(''); setAudioPath(null); setAccessibilityReport(null); setEpubPath(null); setPdfPath(null); }}
                        className="w-full py-3 px-4 rounded-xl font-semibold text-white bg-gray-500 hover:bg-gray-600 transition duration-150 shadow-md"
                    >
                        Start New Conversion
                    </button>
                </div>
            )}

            {/* Status Bar (Always Visible) */}
            {status && (
                <p className={`text-sm p-3 rounded-md text-center font-medium ${status.includes('Success') ? 'bg-green-100 text-green-700' : status.includes('Failed') || status.includes('error') ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
                    {status}
                </p>
            )}
        </div>
    );
}

export default UploadPage;