from marshmallow import ValidationError as MarshmallowValidationError
from pydantic import ValidationError as PydanticValidationError
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

class NotFoundError(Exception):
    def __init__(self, message="Resource not found"):
        self.message = message

class ConflictError(Exception):
    def __init__(self, message="Conflict"):
        self.message = message

class DomainValidationError(Exception):
    """Business rule / domain validation error (e.g., endDate < startDate)."""
    def __init__(self, message: str, field: str | None = None):
        self.message = message
        self.field = field

def _problem_response(status, title, detail=None, errors=None):
    body = {"status": status, "title": title}
    if detail:
        body["detail"] = detail
    if errors:
        body["errors"] = errors
    return body, status

def validation_problem(errors: dict, detail: str | None = None, status: int = 422):
    return _problem_response(status, "Validation Error", detail=detail, errors=errors)

def _pydantic_errors(e: PydanticValidationError):
    grouped = {}
    for err in e.errors():
        loc = ".".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg")
        grouped.setdefault(loc, []).append(msg)
    return grouped

def register_error_handlers(app):
    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow(err):
        return _problem_response(422, "Validation Error", errors=err.messages)

    @app.errorhandler(PydanticValidationError)
    def handle_pydantic(err):
        return _problem_response(422, "Validation Error", errors=_pydantic_errors(err))

    @app.errorhandler(NotFoundError)
    def handle_not_found(err):
        return {"detail": err.message}, 404

    @app.errorhandler(ConflictError)
    def handle_conflict(err):
        return _problem_response(409, "Conflict", detail=err.message)

    @app.errorhandler(IntegrityError)
    def handle_integrity(err):
        return _problem_response(400, "Bad Request", detail="Integrity constraint violated")

    @app.errorhandler(HTTPException)
    def handle_http(err: HTTPException):
        return _problem_response(err.code or 500, err.name or "HTTP Error", detail=err.description)

    @app.errorhandler(ValueError)
    def handle_value_error(err: ValueError):
        # Treat generic value errors from service validation as 400
        return _problem_response(400, "Bad Request", detail=str(err))

    @app.errorhandler(DomainValidationError)
    def handle_domain_validation(err: DomainValidationError):
        errors = {err.field: [err.message]} if err.field else {"detail": [err.message]}
        return _problem_response(400, "Domain Validation Error", detail=err.message, errors=errors)

    @app.errorhandler(Exception)
    def handle_generic(err):
        app.logger.exception("Unhandled exception: %s", err)
        return _problem_response(500, "Internal Server Error", detail="Unexpected error")