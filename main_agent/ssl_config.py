import os
import ssl
import certifi

def configure_ssl():
    """Configure SSL settings for the application."""
    # Set environment variables
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['CURL_CA_BUNDLE'] = certifi.where()
    
    # Create an unverified SSL context
    context = ssl._create_unverified_context()
    ssl._create_default_https_context = lambda: context

# Configure SSL when the module is imported
configure_ssl()
