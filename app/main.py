from fastapi import FastAPI
from app.logger import get_logger

app = FastAPI(title='AI Financial Research Platform API')
logger = get_logger(__name__)


@app.get('/', tags=['health'])
def read_root() -> dict[str, str]:
    """Return a basic health check response."""
    logger.info('Health check endpoint called')
    return {'status': 'ok', 'message': 'FastAPI is running'}


@app.get('/health', tags=['health'])
def health() -> dict[str, str]:
    logger.debug('Health endpoint hit')
    return {'status': 'healthy'}
