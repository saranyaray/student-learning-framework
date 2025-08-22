"""
Custom exceptions for the Student Learning Framework
"""


class StudentLearningFrameworkError(Exception):
    """Base exception for the Student Learning Framework"""

    pass


class DocumentProcessingError(StudentLearningFrameworkError):
    """Raised when document processing fails"""

    pass


class VectorStoreError(StudentLearningFrameworkError):
    """Raised when vector store operations fail"""

    pass


class AgentError(StudentLearningFrameworkError):
    """Raised when agent operations fail"""

    pass


class RetrievalError(StudentLearningFrameworkError):
    """Raised when document retrieval fails"""

    pass


class ConfigurationError(StudentLearningFrameworkError):
    """Raised when configuration is invalid"""

    pass


class ValidationError(StudentLearningFrameworkError):
    """Raised when input validation fails"""

    pass


class APIError(StudentLearningFrameworkError):
    """Raised when API operations fail"""

    pass


class ModelError(StudentLearningFrameworkError):
    """Raised when LLM model operations fail"""

    pass
