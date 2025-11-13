"""
Vercel serverless function handler for Django
"""
import os
import sys
import traceback
from pathlib import Path
from io import BytesIO

# Add the project directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_proj.settings")

# Initialize Django application (do this once at module level)
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    django_loaded = True
    django_error = None
    django_traceback = None
except Exception as e:
    django_loaded = False
    django_error = str(e)
    django_traceback = traceback.format_exc()

def handler(request):
    """
    Vercel serverless function handler
    """
    try:
        # Check if Django loaded successfully
        if not django_loaded:
            error_html = f"""
            <html>
            <head><title>Django Initialization Error</title></head>
            <body>
                <h1>Django Initialization Error</h1>
                <p><strong>Error:</strong> {django_error}</p>
                <h2>Common Issues:</h2>
                <ul>
                    <li><strong>Database Error:</strong> SQLite doesn't work on Vercel. You need PostgreSQL.</li>
                    <li><strong>Missing Environment Variables:</strong> Check SECRET_KEY, DEBUG, ALLOWED_HOSTS</li>
                    <li><strong>Import Error:</strong> Check that all dependencies are in requirements.txt</li>
                </ul>
                <h2>Stack Trace:</h2>
                <pre>{django_traceback}</pre>
            </body>
            </html>
            """
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'text/html'},
                'body': error_html
            }
        
        from django.core.handlers.wsgi import WSGIHandler
        
        # Create WSGI handler
        wsgi_handler = WSGIHandler()
        
        # Get request body
        body = b''
        if hasattr(request, 'body'):
            if isinstance(request.body, bytes):
                body = request.body
            elif isinstance(request.body, str):
                body = request.body.encode('utf-8')
        elif hasattr(request, 'get_body'):
            try:
                body = request.get_body()
                if isinstance(body, str):
                    body = body.encode('utf-8')
            except:
                pass
        
        # Get request path - Vercel provides this in different ways
        path = '/'
        if hasattr(request, 'path'):
            path = request.path
        elif hasattr(request, 'url'):
            from urllib.parse import urlparse
            parsed = urlparse(request.url)
            path = parsed.path
        elif hasattr(request, 'rawPath'):
            path = request.rawPath
        
        if not path or path == '':
            path = '/'
        
        # Get query string
        query_string = ''
        if hasattr(request, 'query_string'):
            if isinstance(request.query_string, bytes):
                query_string = request.query_string.decode('utf-8')
            else:
                query_string = str(request.query_string)
        elif hasattr(request, 'url') and '?' in request.url:
            query_string = request.url.split('?', 1)[1]
        elif hasattr(request, 'rawQuery'):
            query_string = request.rawQuery
        
        # Get headers
        headers = {}
        if hasattr(request, 'headers'):
            headers = dict(request.headers) if hasattr(request.headers, 'items') else request.headers
        
        # Get host
        host = headers.get('host', 'localhost')
        host_parts = host.split(':')
        
        # Get method
        method = getattr(request, 'method', 'GET')
        
        # Build WSGI environ
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'SCRIPT_NAME': '',
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': headers.get('content-type', ''),
            'CONTENT_LENGTH': str(len(body)),
            'SERVER_NAME': host_parts[0],
            'SERVER_PORT': host_parts[1] if len(host_parts) > 1 else '80',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https' if headers.get('x-forwarded-proto') == 'https' else 'http',
            'wsgi.input': BytesIO(body),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        # Add headers to environ
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
        
        # Process request
        response_body = wsgi_handler(environ, start_response)
        
        # Convert response body to bytes
        if isinstance(response_body, list):
            response_content = b''.join([
                chunk if isinstance(chunk, bytes) else str(chunk).encode('utf-8')
                for chunk in response_body
            ])
        else:
            response_content = response_body if isinstance(response_body, bytes) else str(response_body).encode('utf-8')
        
        # Convert headers to dict
        headers_dict = {}
        for header in response_headers:
            if len(header) >= 2:
                headers_dict[header[0]] = header[1]
        
        # Return Vercel response
        return {
            'statusCode': response_status[0],
            'headers': headers_dict,
            'body': response_content.decode('utf-8', errors='replace')
        }
        
    except Exception as e:
        # Return error response with detailed information
        error_trace = traceback.format_exc()
        error_html = f"""
        <html>
        <head><title>Handler Error</title></head>
        <body>
            <h1>Handler Error</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <h2>Stack Trace:</h2>
            <pre>{error_trace}</pre>
            <h2>Troubleshooting:</h2>
            <ul>
                <li>Check Vercel function logs for more details</li>
                <li>Verify all environment variables are set correctly</li>
                <li>Ensure database connection is configured (PostgreSQL required for Vercel)</li>
                <li>Check that all dependencies are in requirements.txt</li>
            </ul>
        </body>
        </html>
        """
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': error_html
        }
