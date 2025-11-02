import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

def create_app(static_folder=None, static_url_path=None):
    # Create app instance with custom static paths for serving processed files
    app = Flask(
        __name__, 
        static_folder=static_folder, 
        static_url_path=static_url_path
    )
    CORS(app)  # Enable Cross-Origin Resource Sharing

    # Initialize Flask-RESTful API
    api = Api(app)

    # Import and Register API Resources (Endpoints)
    from .api.conversion import Upload, DownloadEPUB, DownloadPDF, ServeFile # <-- NEW: Import ServeFile
    
    api.add_resource(Upload, '/api/upload')
    api.add_resource(ServeFile, '/api/result/<string:filename>')  # <-- NEW: Serve files endpoint
    
    api.add_resource(DownloadEPUB, '/api/download/epub/<string:filename>') 
    api.add_resource(DownloadPDF, '/api/download/pdf/<string:filename>') # <-- NEW: Register PDF endpoint
    
    return app
