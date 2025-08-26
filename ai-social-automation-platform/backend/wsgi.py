# """
# WSGI Entry Point for VelocityPost.ai Production Deployment
# Use this file for deploying with Gunicorn, uWSGI, or other WSGI servers
# """

# import os
# import sys
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Add the project directory to the Python path
# sys.path.insert(0, os.path.dirname(__file__))

# # Import the Flask app
# from app import create_app

# # Create the WSGI application
# application = create_app()

# if __name__ == "__main__":
#     # This allows running the WSGI file directly for testing
#     port = int(os.getenv('PORT', 5000))
#     application.run(host='0.0.0.0', port=port, debug=False)