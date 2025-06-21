# Global variable to store JWT token across all modules
JWT_TOKEN_GLOBAL = None

def set_jwt_token_global(token):
    """Set the global JWT token"""
    global JWT_TOKEN_GLOBAL
    JWT_TOKEN_GLOBAL = token

def get_jwt_token_global():
    """Get the global JWT token"""
    return JWT_TOKEN_GLOBAL 