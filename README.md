# Accessibility Learning Hub

The Accessibility Learning Hub is an AI-powered educational technology platform designed to make learning materials inclusive and accessible for everyone, regardless of ability. By leveraging advanced AI, this tool automatically processes educational content from various formats—including PDFs, DOCX files, and YouTube videos—and transforms it into accessible, personalized learning experiences.

## Key Features

- **Multi-Format Processing**: Upload **PDFs**, **DOCX files**, or provide a **YouTube URL** to get started.
- **AI-Powered Simplification**: Complex text is simplified to improve readability for a wider audience.
- **Multilingual Support**: Content can be translated into multiple languages, including Spanish, Tamil, Telugu, and Kannada.
- **Image Accessibility (OCR)**: Automatically extracts images from documents and uses Optical Character Recognition (OCR) to generate descriptive alt-text, making visual content accessible.
- **LaTeX to MathML**: Converts complex LaTeX mathematical equations into accessible MathML for screen readers.
- **Text-to-Speech (TTS)**: Generates audio versions of the processed content, allowing for auditory learning.
- **Export Options**: Download the accessible content as an **EPUB** or **PDF**.
- **Accessibility Themes**:
  - **Dyslexic-Friendly Font**: Switches the UI to a font designed to be easier to read for people with dyslexia.
  - **Color Inversion**: Inverts the color scheme to reduce eye strain and improve readability for users with certain visual impairments.
- **Accessibility Report**: Generates a report analyzing the accessibility of the processed content.

## Technology Stack

### Frontend
- **React.js**: For building the user interface.
- **Vite**: As the frontend build tool.
- **Tailwind CSS**: For styling the application.

### Backend
- **Python**: The core language for the backend logic.
- **Flask**: As the web server and API framework.
- **PyMuPDF & python-docx**: For parsing PDF and DOCX files.
- **Pytesseract & OpenCV**: For performing OCR on images.
- **gTTS & googletrans**: For Text-to-Speech and language translation.
- **yt-dlp**: For fetching content from YouTube videos.
- **SymPy**: For converting LaTeX to MathML.

## Setup and Installation

### Prerequisites
- **Node.js** and **npm**: For running the frontend.
- **Python 3.x**: For running the backend.
- **Tesseract-OCR**: The OCR engine must be installed on your system. You can download it from the [official Tesseract repository](https://github.com/tesseract-ocr/tesseract).

### Backend Setup

1.  **Navigate to the project root** and create a Python virtual environment:
    ```bash
    python -m venv .venv
    ```

2.  **Activate the virtual environment**:
    - On Windows (PowerShell):
      ```powershell
      # If you get a script execution error, first run:
      # Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
      .\.venv\Scripts\Activate.ps1
      ```
    - On macOS/Linux:
      ```bash
      source .venv/bin/activate
      ```

3.  **Install the required Python packages**:
    ```bash
    pip install -r backend/requirements.txt
    ```
    *(Note: A `requirements.txt` file should be created with all the necessary packages like Flask, pytesseract, etc.)*

4.  **Run the backend server**:
    (Make sure your terminal is in the `backend` directory)
    ```bash
    cd backend
    python wsgi.py
    ```
    The backend server will start on `http://127.0.0.1:5000`.

### Frontend Setup

1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```

2.  **Install the npm dependencies**:
    ```bash
    npm install
    ```

3.  **Run the frontend development server**:
    ```bash
    npm run dev
    ```
    The frontend will be available at `http://localhost:5173` (or another port if 5173 is busy).

## How to Use

1.  Open the web application in your browser.
2.  Drag and drop a PDF or DOCX file onto the upload area, or paste a YouTube URL into the input field.
3.  Select the desired output language from the dropdown menu.
4.  Click the "Generate Accessible Version" button.
5.  The system will process the content and provide you with a simplified HTML view, a downloadable audio file, and other export options.
6.  Use the accessibility settings in the top-right corner to toggle the dyslexic-friendly font or color inversion themes.
