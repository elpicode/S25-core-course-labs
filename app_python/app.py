from datetime import datetime
import logging
import os
import sys
import pytz
from flask import Flask, render_template, request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Setup logging
log_dir = '/home/appuser/logs'
# Create log directory if it doesn't exist (for local development)
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
INDEX_REQUEST_COUNT = Counter('app_index_request_count', 'Number of requests to the index page')
HEALTH_REQUEST_COUNT = Counter('app_health_request_count', 'Number of requests to the health endpoint')
ERROR_COUNT = Counter('app_error_count', 'Number of errors encountered', ['type'])
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency in seconds', ['endpoint'])


@app.route("/")
def index():
    """Display current Moscow time."""
    INDEX_REQUEST_COUNT.inc()
    with REQUEST_LATENCY.labels('index').time():
        logger.info("Index page accessed by %s", request.remote_addr)
        moscow_tz = pytz.timezone("Europe/Moscow")
        moscow_time = datetime.now(moscow_tz)
        return render_template("index.html", current_time=moscow_time)


@app.route("/health")
def health():
    """Health check endpoint."""
    HEALTH_REQUEST_COUNT.inc()
    with REQUEST_LATENCY.labels('health').time():
        logger.info("Health check performed")
        return {"status": "healthy"}, 200


@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    ERROR_COUNT.labels('404').inc()
    logger.error("404 error: %s - %s", request.path, e)
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    ERROR_COUNT.labels('500').inc()
    logger.error("500 error: %s", e)
    return render_template("500.html"), 500


if __name__ == "__main__":
    logger.info("Application starting")
    app.run(debug=True, host="0.0.0.0")