import React, { useState } from 'react';
import { useAccessibility } from '../AccessibilityContext'; 
import { ChevronDown, FileText, Loader, Zap, Download, Globe } from 'lucide-react';
import ToggleSwitch from '../components/ToggleSwitch'; // Import the new component
import "./UploadPage.css";


// --- API CONSTANTS ---
const API_BASE_URL = 'http://127.0.0.1:5000';
const UPLOAD_API_URL = `${API_BASE_URL}/api/upload`;
const RESULT_API_URL = `${API_BASE_URL}/api/result`;
// --------------------

// --- MULTILINGUAL SUPPORT ---
const LANGUAGES = {
    'en': 'English',
    'es': 'Español (Spanish)',
    'fr': 'Français (French)',
    'de': 'Deutsch (German)',
    'hi': 'हिन्दी (Hindi)',
    'ta': 'தமிழ் (Tamil)',
    'te': 'తెలుగు (Telugu)',
    'kn': 'ಕನ್ನಡ (Kannada)',
};

const UI_STRINGS = {
    en: {
        title: "Choose or Drag & Drop your Educational Material",
        dropHint: "PDF, DOCX files or YouTube URLs (with transcripts)",
        dropActive: "✨ Drop your file or YouTube URL here!",
        youtubeLabel: "Or paste a YouTube URL (transcript will be extracted):",
        youtubePlaceholder: "https://www.youtube.com/watch?v=...",
        invalidUrl: "Please enter a valid YouTube URL",
        generateButton: "Generate Accessible Version",
        processingDoc: "Processing Document...",
        processingYT: "Processing YouTube Video...",
        docType: "(Document)",
        ytType: "(YouTube + Audio)",
        conversionComplete: "✅ Conversion Complete!",
        audioPlayback: "🔊 Audio Playback",
        downloadAudio: "Download Audio (MP3)",
        simplifiedContent: "📖 Simplified Content Viewer",
        startNew: "Start New Conversion",
        fileSelected: "File selected:",
        urlEntered: "YouTube URL entered:",
        selectFileOrUrl: "Please select a file or enter a YouTube URL first.",
        selectPDFOrDocx: "Please select a PDF or DOCX file.",
        dropInvalid: "Please drop a valid file (PDF/DOCX) or YouTube URL.",
        languageSelector: "Language",
    },
    es: {
        title: "Elija o Arrastre y Suelte su Material Educativo",
        dropHint: "Archivos PDF, DOCX o URLs de YouTube (con transcripciones)",
        dropActive: "✨ ¡Suelte su archivo o URL de YouTube aquí!",
        youtubeLabel: "O pegue una URL de YouTube (se extraerá la transcripción):",
        youtubePlaceholder: "https://www.youtube.com/watch?v=...",
        invalidUrl: "Por favor, ingrese una URL de YouTube válida",
        generateButton: "Generar Versión Accesible",
        processingDoc: "Procesando Documento...",
        processingYT: "Procesando Video de YouTube...",
        docType: "(Documento)",
        ytType: "(YouTube + Audio)",
        conversionComplete: "✅ ¡Conversión Completa!",
        audioPlayback: "🔊 Reproducción de Audio",
        downloadAudio: "Descargar Audio (MP3)",
        simplifiedContent: "📖 Visor de Contenido Simplificado",
        startNew: "Iniciar Nueva Conversión",
        fileSelected: "Archivo seleccionado:",
        urlEntered: "URL de YouTube ingresada:",
        selectFileOrUrl: "Por favor, seleccione un archivo o ingrese una URL de YouTube primero.",
        selectPDFOrDocx: "Por favor, seleccione un archivo PDF o DOCX.",
        dropInvalid: "Por favor, suelte un archivo válido (PDF/DOCX) o URL de YouTube.",
        languageSelector: "Idioma",
    },
    // Add stubs for other languages to prevent errors and provide some feedback
    fr: {
        title: "Choisissez ou glissez-déposez votre matériel pédagogique",
        dropHint: "Fichiers PDF, DOCX ou URL YouTube",
        youtubeLabel: "Ou collez une URL YouTube :",
        generateButton: "Générer une version accessible",
        languageSelector: "Langue",
    },
    de: {
        title: "Wählen oder ziehen Sie Ihr Lehrmaterial per Drag & Drop",
        dropHint: "PDF-, DOCX-Dateien oder YouTube-URLs",
        youtubeLabel: "Oder fügen Sie eine YouTube-URL ein:",
        generateButton: "Barrierefreie Version erstellen",
        languageSelector: "Sprache",
    },
    hi: {
        title: "अपनी शैक्षिक सामग्री चुनें या खींचें और छोड़ें",
        dropHint: "पीडीएफ, DOCX फाइलें या यूट्यूब यूआरएल",
        youtubeLabel: "या एक यूट्यूब यूआरएल पेस्ट करें:",
        generateButton: "सुलभ संस्करण उत्पन्न करें",
        languageSelector: "भाषा",
    },
    ta: {
        title: "உங்கள் கல்விப் பொருளைத் தேர்வுசெய்யவும் அல்லது இழுத்து விடவும்",
        dropHint: "PDF, DOCX கோப்புகள் அல்லது YouTube URLகள்",
        youtubeLabel: "அல்லது ஒரு YouTube URL ஐ ஒட்டவும்:",
        generateButton: " அணுகக்கூடிய பதிப்பை உருவாக்கவும்",
        languageSelector: "மொழி",
    },
    te: {
        title: "మీ విద్యా సామగ్రిని ఎంచుకోండి లేదా లాగండి మరియు వదలండి",
        dropHint: "PDF, DOCX ఫైళ్లు లేదా YouTube URLలు",
        youtubeLabel: "లేదా ఒక YouTube URLను అతికించండి:",
        generateButton: "ప్రాప్యత సంస్కరణను రూపొందించండి",
        languageSelector: "భాష",
    },
    kn: {
        title: "ನಿಮ್ಮ ಶೈಕ್ಷಣಿಕ ಸಾಮಗ್ರಿಯನ್ನು ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ಎಳೆದು ಹಾಕಿ",
        dropHint: "PDF, DOCX ಫೈಲ್‌ಗಳು ಅಥವಾ YouTube URLಗಳು",
        youtubeLabel: "ಅಥವಾ YouTube URL ಅನ್ನು ಅಂಟಿಸಿ:",
        generateButton: "ಪ್ರವೇಶಿಸಬಹುದಾದ ಆವೃತ್ತಿಯನ್ನು ರಚಿಸಿ",
        languageSelector: "ಭಾಷೆ",
    }
};
// ---------------------------

// A helper to merge incomplete translations with English fallback
const getTranslatedStrings = (lang) => {
    const defaultStrings = UI_STRINGS.en;
    const selectedStrings = UI_STRINGS[lang] || defaultStrings;
    return { ...defaultStrings, ...selectedStrings };
};


// NOTE: SettingsPanel component defined locally for single-file operation
const SettingsPanel = () => {
    const { 
        isDyslexicMode, 
        toggleDyslexicMode,
        isHighContrast,
        toggleHighContrast,
        isColorInverted,
        toggleColorInversion
    } = useAccessibility();

    return (
        <div className="absolute top-4 right-4 p-4 bg-gray-100 rounded-lg shadow-lg border w-64">
            <h3 className="text-md font-bold text-gray-800 mb-3 text-center">Accessibility Settings</h3>
            <ToggleSwitch 
                id="dyslexic-toggle"
                isToggled={isDyslexicMode}
                handleToggle={toggleDyslexicMode}
                label="Dyslexic Font"
            />
            <ToggleSwitch 
                id="inversion-toggle"
                isToggled={isColorInverted}
                handleToggle={toggleColorInversion}
                label="Color Inversion"
            />
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
    const [youtubeUrl, setYoutubeUrl] = useState('');
    const [status, setStatus] = useState('');
    const [loading, setLoading] = useState(false);
    const [isDragOver, setIsDragOver] = useState(false);
    const [language, setLanguage] = useState('en');
    
    const [simplifiedHtml, setSimplifiedHtml] = useState(null);
    const [audioPath, setAudioPath] = useState(null);
    const [accessibilityReport, setAccessibilityReport] = useState(null);

    const t = getTranslatedStrings(language);

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
        handleSelectedFile(selectedFile);
    };

    const handleSelectedFile = (selectedFile) => {
        if (selectedFile && (selectedFile.type === 'application/pdf' || 
                            selectedFile.name.endsWith('.docx'))) {
            setFile(selectedFile);
            setYoutubeUrl(''); // Clear YouTube URL when file is selected
            setStatus(`${t.fileSelected} ${selectedFile.name}`);
            setSimplifiedHtml(null);
            setAudioPath(null);
            setAccessibilityReport(null);
        } else {
            setFile(null);
            setStatus(t.selectPDFOrDocx);
        }
    };

    const handleYoutubeUrlChange = (e) => {
        const url = e.target.value;
        setYoutubeUrl(url);
        if (url.trim()) {
            setFile(null); // Clear file when URL is entered
            setStatus(`${t.urlEntered} ${url}`);
            setSimplifiedHtml(null);
            setAudioPath(null);
            setAccessibilityReport(null);
        }
    };

    const isValidYoutubeUrl = (url) => {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/)|youtu\.be\/)[\w-]+/;
        return youtubeRegex.test(url);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragOver(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragOver(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragOver(false);
        
        const droppedText = e.dataTransfer.getData('text');
        const droppedFiles = e.dataTransfer.files;
        
        // Check if it's a YouTube URL
        if (droppedText && isValidYoutubeUrl(droppedText)) {
            setYoutubeUrl(droppedText);
            setFile(null);
            setStatus(`${t.urlEntered} ${droppedText}`);
            setSimplifiedHtml(null);
            setAudioPath(null);
            setAccessibilityReport(null);
        } 
        // Check if it's a file
        else if (droppedFiles.length > 0) {
            handleSelectedFile(droppedFiles[0]);
        }
        else {
            setStatus(t.dropInvalid);
        }
    };

    const handleUpload = async () => {
        if (!file && !youtubeUrl.trim()) {
            setStatus(t.selectFileOrUrl);
            return;
        }

        if (youtubeUrl.trim() && !isValidYoutubeUrl(youtubeUrl)) {
            setStatus(t.invalidUrl);
            return;
        }

        setLoading(true);
        setStatus('Uploading and processing...');

        try {
            const formData = new FormData();
            
            if (file) {
                formData.append('file', file);
            } else if (youtubeUrl.trim()) {
                formData.append('youtube_url', youtubeUrl.trim());
            }
            formData.append('language', language); // Add language to the request

            const response = await fetch(UPLOAD_API_URL, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                let errorData = {};
                try { errorData = await response.json(); } catch (e) { console.error('Parse error:', e); }
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
        <div className="page-container space-y-6">
            {!simplifiedHtml ? (
                // --- UPLOADER VIEW (Enhanced with drag & drop and YouTube support) ---
                <>
                    {/* Language Selector */}
                    <div className="flex justify-center mb-4">
                        <div className="flex items-center gap-2 bg-white p-2 rounded-lg shadow-md border">
                            <Globe className="w-5 h-5 text-gray-500" />
                            <select
                                id="language-select"
                                value={language}
                                onChange={(e) => setLanguage(e.target.value)}
                                className="bg-transparent font-semibold text-gray-700 focus:outline-none"
                            >
                                {Object.entries(LANGUAGES).map(([code, name]) => (
                                    <option key={code} value={code}>{name}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div 
                        className={`p-10 border-4 border-dashed rounded-2xl text-center cursor-pointer transition duration-300 transform shadow-xl ${
                            isDragOver 
                                ? 'border-green-500 bg-green-50 scale-[1.02]' 
                                : 'border-indigo-300 bg-indigo-50 hover:border-purple-500 hover:scale-[1.01]'
                        }`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        <FileText className="w-12 h-12 text-indigo-500 mx-auto mb-4" />
                        <input 
                            type="file" 
                            onChange={handleFileChange} 
                            accept=".pdf,.docx"
                            className="hidden" 
                            id="file-upload"
                        />
                        <label htmlFor="file-upload" className="block text-xl font-bold text-gray-700 cursor-pointer mb-4">
                            {file ? `📄 ${file.name}` : t.title}
                        </label>
                        <p className="text-sm text-indigo-400 mb-4">
                            {isDragOver ? t.dropActive : t.dropHint}
                        </p>
                        
                        {/* YouTube URL Input */}
                        <div className="mt-6 max-w-md mx-auto">
                            <label htmlFor="youtube-url" className="block text-sm font-medium text-gray-700 mb-2">
                                {t.youtubeLabel}
                            </label>
                            <input
                                type="url"
                                id="youtube-url"
                                value={youtubeUrl}
                                onChange={handleYoutubeUrlChange}
                                placeholder={t.youtubePlaceholder}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            />
                            {youtubeUrl && !isValidYoutubeUrl(youtubeUrl) && (
                                <p className="text-red-500 text-xs mt-1">{t.invalidUrl}</p>
                            )}
                        </div>
                    </div>

                    <button
                        onClick={handleUpload}
                        disabled={(!file && !youtubeUrl.trim()) || loading || (youtubeUrl.trim() && !isValidYoutubeUrl(youtubeUrl))}
                        className={`w-full py-4 px-6 rounded-xl font-extrabold text-white text-lg shadow-lg transition duration-200 transform hover:scale-[1.005] 
                          ${(!file && !youtubeUrl.trim()) || loading || (youtubeUrl.trim() && !isValidYoutubeUrl(youtubeUrl))
                            ? 'bg-gray-400 cursor-not-allowed shadow-none' 
                            : 'bg-purple-600 hover:bg-purple-700 focus:ring-4 focus:ring-purple-300'
                          }`}
                    >
                        {loading ? (
                            <span className="flex items-center justify-center">
                                <Loader className="w-5 h-5 mr-2 animate-spin" /> 
                                {file ? t.processingDoc : t.processingYT}
                            </span>
                        ) : (
                            `🚀 ${t.generateButton} ${file ? t.docType : youtubeUrl ? t.ytType : ''}`
                        )}
                    </button>
                </>
            ) : (
                // --- RESULTS VIEW (Clean and organized) ---
                <div className={resultsClasses}>
                    
                    <SettingsPanel />

                    <h2 className="text-2xl font-bold text-purple-700 border-b pb-2">{t.conversionComplete}</h2>
                    
                    {accessibilityReport && <ReportDisplay report={accessibilityReport} />}
                    
                    {/* Audio Controls - RESTORED VISIBLE AUDIO TAG */}
                    {audioPath && (
                        <div className="p-4 border rounded-lg bg-white shadow-md">
                            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2 text-gray-700">
                                {t.audioPlayback}
                            </h3>
                            <audio controls src={audioPath} className="w-full rounded-md shadow-inner">
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                    )}
                    
                    {/* DOWNLOAD BUTTONS */}
                    <div className="flex flex-col sm:flex-row gap-4 p-4 border rounded-xl bg-purple-50 shadow-inner">
                        {/* Audio Download */}
                        {audioPath && (
                            <a href={audioPath} download className="flex-1">
                                <button className="w-full py-3 px-4 flex items-center justify-center gap-2 rounded-xl font-semibold text-indigo-700 border border-indigo-500 bg-white hover:bg-indigo-50 transition duration-150 shadow-md">
                                    <span role="img" aria-label="Audio download">🎧</span> {t.downloadAudio}
                                </button>
                            </a>
                        )}
                    </div>
                    
                    {/* Simplified Content Viewer */}
                    <div className="p-0">
                        <h3 className="text-lg font-semibold mb-2 flex items-center gap-2 text-gray-700">
                            <span role="img" aria-label="Book emoji">📖</span> {t.simplifiedContent}
                        </h3>
                        
                        <div className={contentClasses}>
                            <div 
                                className="text-gray-800"
                                dangerouslySetInnerHTML={{ __html: simplifiedHtml }}
                            />
                        </div>
                    </div>

                    <button
                        onClick={() => { 
                            setSimplifiedHtml(null); 
                            setFile(null); 
                            setYoutubeUrl(''); 
                            setStatus(''); 
                            setAudioPath(null); 
                            setAccessibilityReport(null); 
                        }}
                        className="w-full py-3 px-4 rounded-xl font-semibold text-white bg-gray-500 hover:bg-gray-600 transition duration-150 shadow-md"
                    >
                        {t.startNew}
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