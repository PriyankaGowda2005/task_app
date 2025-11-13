"""
Vercel serverless function handler for Django
This file should be in the api/ directory for Vercel to recognize it
"""
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_proj.settings")

from django.core.wsgi import get_wsgi_application

# Initialize Django application
application = get_wsgi_application()

# Handler function for Vercel
def handler(request):
    """
    Vercel serverless function handler
    """
    from django.core.handlers.wsgi import WSGIHandler
    from io import BytesIO
    
    # Create WSGI handler
    wsgi_handler = WSGIHandler()
    
    # Get request body
    body = b''
    if hasattr(request, 'body'):
        if isinstance(request.body, bytes):
            body = request.body
        elif isinstance(request.body, str):
            body = request.body.encode()
    elif hasattr(request, 'get_body'):
        body = request.get_body()
        if isinstance(body, str):
            body = body.encode()
    
    # Build WSGI environ from Vercel request
    host = request.headers.get('host', 'localhost')
    host_parts = host.split(':')
    
    environ = {
        'REQUEST_METHOD': request.method,
        'PATH_INFO': request.path,
        'QUERY_STRING': getattr(request, 'query_string', b'').decode() if hasattr(request, 'query_string') else '',
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)),
        'SERVER_NAME': host_parts[0],
        'SERVER_PORT': host_parts[1] if len(host_parts) > 1 else '80',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https' if request.headers.get('x-forwarded-proto') == 'https' else 'http',
        'wsgi.input': BytesIO(body),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add headers to environ
    for key, value in request.headers.items():
        key_upper = key.upper().replace('-', '_')
        if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key_upper}'] = value
    
    # Response status and headers
    response_status = [200]
    response_headers = []
    
    def start_response(status, headers):
        response_status[0] = int(status.split()[0])
        response_headers[:] = headers
    
    # Process request
    response_body = wsgi_handler(environ, start_response)
    
    # Convert response body to bytes
    if isinstance(response_body, list):
        response_content = b''.join([
            chunk if isinstance(chunk, bytes) else chunk.encode() 
            for chunk in response_body
        ])
    else:
        response_content = response_body if isinstance(response_body, bytes) else response_body.encode()
    
    # Return Vercel response - Vercel Python runtime expects a dict
    return {
        'statusCode': response_status[0],
        'headers': dict(response_headers),
        'body': response_content.decode('utf-8', errors='replace')
    }
