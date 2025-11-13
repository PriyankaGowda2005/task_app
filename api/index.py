"""
Vercel serverless function handler for Django
This file should be in the api/ directory for Vercel to recognize it
"""
import os
import sys
import traceback
import json
from pathlib import Path
from io import BytesIO

# Add the project directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_proj.settings")

# Initialize Django application (do this once at module level)
django_loaded = False
django_error = None
django_traceback = None
application = None

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    django_loaded = True
except Exception as e:
    django_loaded = False
    django_error = str(e)
    django_traceback = traceback.format_exc()
    # Print to stderr so it shows in Vercel logs
    print(f"Django initialization failed: {e}", file=sys.stderr)
    print(django_traceback, file=sys.stderr)

def handler(request):
    """
    Vercel serverless function handler
    Vercel Python runtime passes request as an object with specific attributes
    """
    try:
        # Check if Django loaded successfully
        if not django_loaded:
            error_msg = f"Django initialization error: {django_error}\n\n{django_traceback}"
            print(error_msg, file=sys.stderr)
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'text/plain; charset=utf-8'},
                'body': error_msg
            }
        
        # Import here to avoid issues if Django didn't load
        from django.core.handlers.wsgi import WSGIHandler
        from urllib.parse import urlparse, parse_qs
        
        # Create WSGI handler
        wsgi_handler = WSGIHandler()
        
        # Safely extract request attributes
        # Vercel Python runtime provides request as an object
        try:
            # Try to get method
            method = 'GET'
            if hasattr(request, 'method'):
                method = request.method
            elif hasattr(request, 'get') and callable(request.get):
                method = request.get('method', 'GET')
            
            # Try to get path
            path = '/'
            if hasattr(request, 'path'):
                path = request.path
            elif hasattr(request, 'url'):
                parsed = urlparse(request.url)
                path = parsed.path
            elif hasattr(request, 'get') and callable(request.get):
                path = request.get('path', '/')
            
            # Ensure path starts with /
            if not path or not path.startswith('/'):
                path = '/' + path.lstrip('/')
            
            # Try to get query string
            query_string = ''
            if hasattr(request, 'query_string'):
                query_string = request.query_string if isinstance(request.query_string, str) else request.query_string.decode('utf-8')
            elif hasattr(request, 'url') and '?' in str(request.url):
                query_string = str(request.url).split('?', 1)[1]
            elif hasattr(request, 'get') and callable(request.get):
                query_string = request.get('query_string', '')
            
            # Try to get headers
            headers = {}
            if hasattr(request, 'headers'):
                if isinstance(request.headers, dict):
                    headers = request.headers
                elif hasattr(request.headers, 'items'):
                    headers = dict(request.headers.items())
                elif hasattr(request.headers, 'get'):
                    # Headers might be a case-insensitive dict
                    headers = {k: request.headers.get(k) for k in request.headers}
            elif hasattr(request, 'get') and callable(request.get):
                headers = request.get('headers', {})
            
            # Try to get body
            body = b''
            if hasattr(request, 'body'):
                if isinstance(request.body, bytes):
                    body = request.body
                elif isinstance(request.body, str):
                    body = request.body.encode('utf-8')
            elif hasattr(request, 'get') and callable(request.get):
                body_data = request.get('body', '')
                if isinstance(body_data, bytes):
                    body = body_data
                elif isinstance(body_data, str):
                    body = body_data.encode('utf-8')
            
            # Get host
            host = headers.get('host', headers.get('Host', 'localhost'))
            host_parts = str(host).split(':')
            
            # Determine scheme
            scheme = 'https'
            if headers.get('x-forwarded-proto'):
                scheme = headers.get('x-forwarded-proto')
            elif headers.get('X-Forwarded-Proto'):
                scheme = headers.get('X-Forwarded-Proto')
            
            # Build WSGI environ
            environ = {
                'REQUEST_METHOD': str(method),
                'PATH_INFO': str(path),
                'SCRIPT_NAME': '',
                'QUERY_STRING': str(query_string),
                'CONTENT_TYPE': headers.get('content-type', headers.get('Content-Type', '')),
                'CONTENT_LENGTH': str(len(body)),
                'SERVER_NAME': host_parts[0],
                'SERVER_PORT': host_parts[1] if len(host_parts) > 1 else ('443' if scheme == 'https' else '80'),
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': scheme,
                'wsgi.input': BytesIO(body),
                'wsgi.errors': sys.stderr,
                'wsgi.multithread': False,
                'wsgi.multiprocess': True,
                'wsgi.run_once': False,
            }
            
            # Add headers to environ (WSGI format)
            for key, value in headers.items():
                key_upper = key.upper().replace('-', '_')
                if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                    environ[f'HTTP_{key_upper}'] = str(value)
            
            # Response status and headers
            response_status = [200]
            response_headers = []
            
            def start_response(status, headers_list):
                response_status[0] = int(status.split()[0])
                response_headers[:] = headers_list
            
            # Process request through Django
            response_body = wsgi_handler(environ, start_response)
            
            # Convert response body to bytes
            if isinstance(response_body, list):
                response_content = b''.join([
                    chunk if isinstance(chunk, bytes) else str(chunk).encode('utf-8')
                    for chunk in response_body
                ])
            else:
                response_content = response_body if isinstance(response_body, bytes) else str(response_body).encode('utf-8')
            
            # Convert headers to dict (lowercase keys for HTTP)
            headers_dict = {}
            for header in response_headers:
                if len(header) >= 2:
                    headers_dict[header[0].lower()] = str(header[1])
            
            # Return Vercel response format
            return {
                'statusCode': response_status[0],
                'headers': headers_dict,
                'body': response_content.decode('utf-8', errors='replace')
            }
            
        except AttributeError as e:
            # Request object doesn't have expected attributes
            error_msg = f"Request object error: {e}\nRequest type: {type(request)}\nRequest dir: {dir(request)[:20]}\n\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'text/plain; charset=utf-8'},
                'body': f"Request handling error: {e}"
            }
            
    except Exception as e:
        # Catch-all for any other errors
        error_trace = traceback.format_exc()
        error_msg = f"Handler error: {e}\n\n{error_trace}"
        print(error_msg, file=sys.stderr)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain; charset=utf-8'},
            'body': f"Internal Server Error: {e}"
        }
