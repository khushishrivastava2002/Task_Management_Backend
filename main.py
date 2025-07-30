from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from config.database import init_db
from auth.routers import auth_router, docs_auth_dependency
from auth.services import validate_api_key
import uvicorn
from user_auth.routers import user_auth_router
from fastapi.middleware.cors import CORSMiddleware

####################################################################################################################
############ fastAPI lifespan that handle database on_event is depreacted ##########################################


"""
@asynccontextmanager is a decorator from Python's contextlib module that allows you to create an asynchronous context manager using a generator function.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI application.
    This replaces the deprecated @app.on_event("startup") and @app.on_event("shutdown")
    """
    # Startup events
    await init_db()
    print("Database initialized with Beanie ODM")
    
    yield  # This separates startup from shutdown events
    
    # Shutdown events (if needed)
    print("Application shutting down...")

##############################################################################################################################

app = FastAPI(
    title="Secure API with Authentication",
    version="1.0.0",
    root_path="/task_manager",
    description="Fast APi for the Task Manager by which any one can manage there tasks and lot a task to another person",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    lifespan=lifespan, 
    contact={
        "name": "Khushi Shrivastava",
        "email": "shrivastavakhushi419@gmail.com",
    }
)

security = HTTPBearer(auto_error=False)

"""
--- By default, when you use HTTPBearer as a dependency (e.g., Depends(security)), FastAPI automatically raises an HTTPException with a 401 (Unauthorized) status code if the Authorization header is missing or invalid.

--- Setting auto_error=False disables this automatic error handling. Instead of raising an exception automatically, it allows you to manually handle the authentication logic and decide what to do if the token is missing or invalid.

"""

##################################################################################################
############ CORSMiddleware ######################################################################  


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

############################################################################################################
###################### Include auth router #################################################################

app.include_router(auth_router)
app.include_router(user_auth_router)

##############################################################################################################
#################### Custom docs with built-in authentication form ###########################################

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(
    token: str = Query(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Protected Swagger UI docs with authentication form"""
    
    # Check if token is provided in query parameter
    api_key = None
    if token:
        api_key = token
    elif credentials:
        api_key = credentials.credentials
    
    # If no API key provided, show login form
    if not api_key:
        return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>API Documentation - Authentication Required</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                    .container { background: #f5f5f5; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .form-group { margin-bottom: 15px; }
                    label { display: block; margin-bottom: 5px; font-weight: bold; }
                    input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
                    button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
                    button:hover { background: #0056b3; }
                    .error { color: red; margin-top: 10px; }
                    .info { background: #e7f3ff; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
                    .loading { display: none; color: #007bff; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>API Documentation Access</h1>
                    <div class="info">
                        <strong>Authentication Required:</strong> Please enter your API key to access the documentation.
                    </div>
                    
                    <form id="authForm">
                        <div class="form-group">
                            <label for="apiKey">API Key:</label>
                            <input type="text" id="apiKey" name="apiKey" placeholder="sk-your-api-key-here" required>
                        </div>
                        <button type="submit" id="submitBtn">Access Documentation</button>
                        <div class="loading" id="loading">Validating API key...</div>
                    </form>
                    
                    <div id="error" class="error" style="display: none;"></div>
                    
                    <hr style="margin: 30px 0;">
                    <h3>Don't have an API key?</h3>
                    <p>Create one using this command:</p>
                    <code style="background: #f0f0f0; padding: 10px; display: block; border-radius: 4px;">
                    curl -X POST "http://localhost:8000/auth/api-keys" -H "Content-Type: application/json" -d '{"name": "my-key"}'
                    </code>
                </div>

                <script>
                    document.getElementById('authForm').addEventListener('submit', async function(e) {
                        e.preventDefault();
                        const apiKey = document.getElementById('apiKey').value;
                        const errorDiv = document.getElementById('error');
                        const loadingDiv = document.getElementById('loading');
                        const submitBtn = document.getElementById('submitBtn');
                        
                        if (!apiKey) {
                            errorDiv.textContent = 'Please enter an API key';
                            errorDiv.style.display = 'block';
                            return;
                        }
                        
                        // Show loading state
                        loadingDiv.style.display = 'block';
                        submitBtn.disabled = true;
                        errorDiv.style.display = 'none';
                        
                        // Validate API key
                        try {
                            const response = await fetch('/protected', {
                                headers: {
                                    'Authorization': `Bearer ${apiKey}`
                                }
                            });
                            
                            if (response.ok) {
                                // Redirect to docs with token in URL
                                window.location.replace(`/swagger-docs?token=${encodeURIComponent(apiKey)}`);
                            } else {
                                errorDiv.textContent = 'Invalid API key. Please check your key and try again.';
                                errorDiv.style.display = 'block';
                                loadingDiv.style.display = 'none';
                                submitBtn.disabled = false;
                            }
                        } catch (error) {
                            errorDiv.textContent = 'Error validating API key. Please try again.';
                            errorDiv.style.display = 'block';
                            loadingDiv.style.display = 'none';
                            submitBtn.disabled = false;
                        }
                    });
                </script>
            </body>
            </html>
                    """)
    
    # Validate the provided API key
    key_doc = await validate_api_key(api_key)
    
    if not key_doc:
        # If invalid API key, redirect back to login form
        return HTMLResponse(content="""
        <script>
            alert('Invalid or expired API key. Redirecting to login...');
            window.location.href = '/docs';
        </script>
        """)
    
    # Redirect to proper swagger docs with token
    return HTMLResponse(content=f"""
    <script>
        window.location.replace('/swagger-docs?token={api_key}');
    </script>
    """)

##############################################################################################################
############# docs with token ################################################################################

@app.get("/swagger-docs", include_in_schema=False)
async def swagger_docs_with_token(token: str):
    """Swagger UI docs with token authentication"""
    
    # Validate the API key
    key_doc = await validate_api_key(token)
    
    if not key_doc:
        return HTMLResponse(content="""
        <script>
            alert('Invalid or expired API key. Redirecting to login...');
            window.location.href = '/docs';
        </script>
        """)
    
    # Return custom HTML with working Swagger UI
    return HTMLResponse(
    content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>API Documentation</title>
            <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css" />
            <style>
                html {{
                    box-sizing: border-box;
                    overflow: -moz-scrollbars-vertical;
                    overflow-y: scroll;
                }}
                *, *:before, *:after {{
                    box-sizing: inherit;
                }}
                body {{
                    margin:0;
                    background: #fafafa;
                }}
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
            <script>
                window.onload = function() {{
                    const ui = SwaggerUIBundle({{
                        url: '/openapi.json?token={token}',
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        plugins: [
                            SwaggerUIBundle.plugins.DownloadUrl
                        ],
                        layout: "StandaloneLayout",
                        persistAuthorization: true,
                        displayRequestDuration: true,
                        filter: true,
                        requestInterceptor: function(request) {{
                            // Add the API key to all requests
                            request.headers['Authorization'] = 'Bearer {token}';
                            return request;
                        }},
                        onComplete: function() {{
                            console.log('Swagger UI loaded successfully');
                        }}
                    }});
                    
                    window.ui = ui;
                }};
            </script>
        </body>
        </html>
    """)

####################################################################################################################
# Simplified OpenAPI endpoint with better error handling

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(token: str = Query(None)):
    """Protected OpenAPI schema"""
    
    # Validate token if provided
    if token:
        key_doc = await validate_api_key(token)
        if not key_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # Generate OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version="3.0.2",
        description=app.description,
        routes=app.routes,
    )
    
    # Ensure components section exists
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "API Key"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"HTTPBearer": []}]
    
    return openapi_schema

##################################################################################################################
# Example protected endpoint

@app.get("/protected")
async def protected_endpoint(current_key = Depends(docs_auth_dependency)):
    """Example protected endpoint"""
    return {
        "message": "This is a protected endpoint",
        "api_key_name": current_key.name,
        "last_used": current_key.last_used
    }


###########################################################################################################################
# Public endpoint to create first API key

@app.get("/")
async def root():
    """Public endpoint with instructions"""
    return {
        "message": "Welcome to Secure API",
        "instructions": [
            "1. Create an API key by POST to /auth/api-keys with {'name': 'your-key-name'}",
            "2. Use the returned API key in Authorization header as 'Bearer your-api-key'",
            "3. Access protected docs at /docs with valid API key",
            "4. All endpoints except /auth/api-keys creation require authentication"
        ]
    }

##################################################################################################################################
# Health check endpoint

@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

####################################################################################################################################
############# Start the backend fastAPI server #####################################################################################

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
#####################################################################################################################################