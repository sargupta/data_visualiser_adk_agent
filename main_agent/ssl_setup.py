import os
import ssl
import certifi
import httpx

def configure_ssl():
    # Set SSL context to use certifi's certificates
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    # Configure environment variables
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    os.environ['SSL_CERT_FILE'] = certifi.where()
    
    # For development only - disable SSL verification
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    ssl._create_default_https_context = ssl._create_unverified_context
    
    return ssl_context

def get_httpx_client():
    # Create an HTTPX client with SSL verification disabled (for development)
    return httpx.AsyncClient(verify=False)
