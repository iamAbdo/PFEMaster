from app import create_app
from config import Config

app = create_app(Config)

if __name__ == '__main__':
    Config.init_app()  # Create necessary directories
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        ssl_context=(Config.SERVER_CERT, Config.SERVER_KEY),
        debug=True
    ) 