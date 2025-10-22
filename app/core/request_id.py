import uuid
from flask import g, request
from app.core.logging import get_logger

REQUEST_ID_HEADER = "X-Request-ID"
log = get_logger()

def init_request_id(app, logger):
    @app.before_request
    def assign_request_id():
        rid = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        g.request_id = rid
        logger.info("request.start", method=request.method, path=request.path, request_id=rid)

    @app.after_request
    def add_header(resp):
        if hasattr(g, "request_id"):
            resp.headers[REQUEST_ID_HEADER] = g.request_id
            logger.info("request.end",
                        method=request.method,
                        path=request.path,
                        status=resp.status_code,
                        request_id=g.request_id)
        return resp