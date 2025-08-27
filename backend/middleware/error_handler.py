from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import logging
from typing import Union

logger = logging.getLogger(__name__)


def add_error_handlers(app: FastAPI) -> None:
    """Add error handlers to the FastAPI application"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        # Convert errors to JSON-serializable format
        errors = []
        for error in exc.errors():
            error_dict = {
                "type": error.get("type"),
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "input": str(error.get("input")) if error.get("input") is not None else None
            }
            errors.append(error_dict)
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": errors
            }
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """Handle Pydantic validation errors"""
        # Convert errors to JSON-serializable format
        errors = []
        for error in exc.errors():
            error_dict = {
                "type": error.get("type"),
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "input": str(error.get("input")) if error.get("input") is not None else None
            }
            errors.append(error_dict)
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "VALIDATION_ERROR", 
                "message": "Data validation failed",
                "details": errors
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handle database errors"""
        logger.error(f"Database error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "DATABASE_ERROR",
                "message": "A database error occurred",
                "details": str(exc) if app.debug else None
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions"""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if app.debug else None
            }
        )