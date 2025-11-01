import os # <-- Must import os
from accessibility_hub import create_app

# Calculate the ABSOLUTE path to the 'backend' directory
# This resolves to C:\accessibility-learning-hub\backend
backend_root_dir = os.path.dirname(os.path.abspath(__file__))

# Pass the absolute path to the 'temp_uploads' folder to the app factory
app = create_app(
    static_folder=os.path.join(backend_root_dir, 'temp_uploads'), 
    static_url_path='/api/result'
) 

if __name__ == '__main__':
    app.run(debug=True)