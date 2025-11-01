from flask import Flask
from flask_restful import Api
from flask_cors import CORS

# Modify create_app to accept static_folder arguments
def create_app(static_folder=None, static_url_path=None):
    # Pass the static folder arguments to the Flask constructor
    app = Flask(__name__, 
                static_folder=static_folder, 
                static_url_path=static_url_path)
    
    CORS(app) 

    api = Api(app)

    # We must remove the custom ResultFile endpoint since Flask's static handler
    # will now manage the /api/result/ path automatically.
    from .api.conversion import Upload
    api.add_resource(Upload, '/api/upload')
    
    return app
