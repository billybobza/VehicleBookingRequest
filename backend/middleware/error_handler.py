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
        logger.warning(f"HTTP {exc.status_code} error on {request.url}: {exc.detail}")
        
        # Provide user-friendly error messages
        user_message = exc.detail
        error_code = f"HTTP_{exc.status_code}"
        
        if exc.status_code == 400:
            error_code = "BAD_REQUEST"
            if "validation" in str(exc.detail).lower():
                user_message = "The request contains invalid data. Please check your inputs."
        elif exc.status_code == 404:
            error_code = "NOT_FOUND"
            user_message = "The requested resource was not found."
        elif exc.status_code == 409:
            error_code = "CONFLICT"
            user_message = "The request conflicts with the current state of the resource."
        elif exc.status_code == 422:
            error_code = "VALIDATION_ERROR"
            user_message = "The request data failed validation. Please check your inputs."
        elif exc.status_code >= 500:
            error_code = "INTERNAL_SERVER_ERROR"
            user_message = "An internal server error occurred. Please try again later."
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": error_code,
                    "message": user_message,
                    "details": exc.detail if exc.status_code < 500 else None
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        logger.warning(f"Validation error on {request.url}: {exc.errors()}")
        
        # Convert errors to JSON-serializable format with user-friendly messages
        errors = []
        for error in exc.errors():
            field_name = error.get("loc", [])[-1] if error.get("loc") else "field"
            error_type = error.get("type", "")
            
            # Create user-friendly error messages
            user_message = error.get("msg", "Invalid value")
            if error_type == "missing":
                user_message = f"{field_name} is required"
            elif error_type == "value_error":
                user_message = f"{field_name} has an invalid value"
            elif error_type == "type_error":
                user_message = f"{field_name} must be of the correct type"
            
            error_dict = {
                "type": error_type,
                "loc": error.get("loc"),
                "msg": user_message,
                "field": field_name,
                "input": str(error.get("input")) if error.get("input") is not None else None
            }
            errors.append(error_dict)
        
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Please check your form inputs. Some fields contain invalid data.",
                    "details": errors
                }
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
        logger.error(f"Database error on {request.url}: {exc}", exc_info=True)
        
        # Determine specific error type
        error_message = "A database error occurred. Please try again later."
        error_code = "DATABASE_ERROR"
        
        if "UNIQUE constraint failed" in str(exc):
            error_message = "This record already exists. Please check your data."
            error_code = "DUPLICATE_RECORD"
        elif "FOREIGN KEY constraint failed" in str(exc):
            error_message = "Referenced data does not exist. Please check your selection."
            error_code = "INVALID_REFERENCE"
        elif "NOT NULL constraint failed" in str(exc):
            error_message = "Required data is missing. Please complete all required fields."
            error_code = "MISSING_REQUIRED_DATA"
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": error_code,
                    "message": error_message,
                    "details": str(exc) if hasattr(app, 'debug') and app.debug else None
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions"""
        logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later or contact support if the problem persists.",
                    "details": str(exc) if hasattr(app, 'debug') and app.debug else None
                }
            }
        )