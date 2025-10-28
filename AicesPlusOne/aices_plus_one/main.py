import uvicorn
import asyncio
import logging
from .api import app
from .config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application"""
    # Create necessary directories
    Config.create_directories()
    
    logger.info("Starting Git Repository Manager")
    
    config = uvicorn.Config(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT,
        log_level=Config.LOG_LEVEL.lower(),
        reload=False
    )
    
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    main()
