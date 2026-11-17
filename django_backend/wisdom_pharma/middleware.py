class ApiTrailingSlashMiddleware:
    """
    Middleware that ensures API requests (/api and /api/...) are routed with a trailing slash
    transparently at the WSGI/ASGI level.

    The React (Vite) frontend sends requests without trailing slashes (e.g. POST /api/auth/login,
    GET /api/medicines, GET /api/categories). By standardizing the request path_info internally,
    Django handles them without HTTP 301/302 redirects, avoiding body payload loss on POST/PUT requests
    and preventing Django CommonMiddleware RuntimeError.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        if (path == '/api' or path.startswith('/api/')) and not path.endswith('/'):
            request.path_info = path + '/'
            if hasattr(request, 'path'):
                request.path = request.path + '/'
        return self.get_response(request)
