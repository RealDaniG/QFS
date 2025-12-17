"""
fatal_errors.py - Typed Fatal Error Hierarchy for QFS V13

Defines a hierarchy of typed fatal exceptions to replace sys.exit() calls.
All exceptions maintain Zero-Simulation compliance and provide auditable logging.
"""

from typing import Optional
from .CertifiedMath import CertifiedMath

class ZeroSimAbort(Exception):
    """
    Base exception for Zero-Simulation violations.
    
    This replaces sys.exit() calls to maintain determinism while still
    signaling fatal situations that would normally terminate the interpreter.
    """
    
    def __init__(self, message: str = "Zero-Simulation abort requested", exit_code: int = 1):
        """
        Initialize a ZeroSimAbort exception.
        
        Args:
            message: Descriptive error message
            exit_code: Exit code that would have been used with sys.exit()
        """
        self.exit_code = exit_code
        super().__init__(f"{message} (exit code: {exit_code})")

class EconomicInvariantBreach(ZeroSimAbort):
    """
    Exception raised when an economic invariant is breached.
    
    Used to signal violations of fundamental economic principles
    that must halt execution to maintain system integrity.
    """
    
    def __init__(self, invariant_name: str, breach_details: str = ""):
        """
        Initialize an EconomicInvariantBreach exception.
        
        Args:
            invariant_name: Name of the violated invariant
            breach_details: Additional details about the breach
        """
        self.invariant_name = invariant_name
        self.breach_details = breach_details
        message = f"Economic invariant '{invariant_name}' breached"
        if breach_details:
            message += f": {breach_details}"
        super().__init__(message, exit_code=10)

class GovernanceGuardFailure(ZeroSimAbort):
    """
    Exception raised when a governance guard fails.
    
    Used to signal violations of governance policies
    that must halt execution to maintain system integrity.
    """
    
    def __init__(self, guard_name: str, failure_details: str = ""):
        """
        Initialize a GovernanceGuardFailure exception.
        
        Args:
            guard_name: Name of the failed guard
            failure_details: Additional details about the failure
        """
        self.guard_name = guard_name
        self.failure_details = failure_details
        message = f"Governance guard '{guard_name}' failed"
        if failure_details:
            message += f": {failure_details}"
        super().__init__(message, exit_code=20)

class ConsensusViolation(ZeroSimAbort):
    """
    Exception raised when a consensus violation occurs.
    
    Used to signal violations of consensus protocols
    that must halt execution to maintain system integrity.
    """
    
    def __init__(self, violation_type: str, node_id: Optional[str] = None):
        """
        Initialize a ConsensusViolation exception.
        
        Args:
            violation_type: Type of consensus violation
            node_id: ID of the violating node (if known)
        """
        self.violation_type = violation_type
        self.node_id = node_id
        message = f"Consensus violation: {violation_type}"
        if node_id:
            message += f" (node: {node_id})"
        super().__init__(message, exit_code=30)

class SecurityBreach(ZeroSimAbort):
    """
    Exception raised when a security breach is detected.
    
    Used to signal security violations that must halt execution
    to maintain system integrity and prevent further damage.
    """
    
    def __init__(self, breach_type: str, severity: str = "high"):
        """
        Initialize a SecurityBreach exception.
        
        Args:
            breach_type: Type of security breach
            severity: Severity level ("low", "medium", "high", "critical")
        """
        self.breach_type = breach_type
        self.severity = severity
        message = f"Security breach detected: {breach_type} (severity: {severity})"
        exit_code = 40 if severity == "critical" else 41
        super().__init__(message, exit_code=exit_code)

class ResourceExhaustion(ZeroSimAbort):
    """
    Exception raised when system resources are exhausted.
    
    Used to signal resource exhaustion that must halt execution
    to maintain system stability.
    """
    
    def __init__(self, resource_type: str, limit: Optional[int] = None):
        """
        Initialize a ResourceExhaustion exception.
        
        Args:
            resource_type: Type of exhausted resource
            limit: Resource limit that was exceeded (if applicable)
        """
        self.resource_type = resource_type
        self.limit = limit
        message = f"Resource exhaustion: {resource_type}"
        if limit is not None:
            message += f" (limit: {limit})"
        super().__init__(message, exit_code=50)

# Utility functions for auditable exception handling
def log_fatal_exception(exception: Exception, context: Optional[str] = None) -> None:
    """
    Log a fatal exception through CertifiedMath's logging context.
    
    Args:
        exception: The exception to log
        context: Additional context information
    """
    log_entry = {
        "type": "FATAL_EXCEPTION",
        "exception_type": type(exception).__name__,
        "message": str(exception),
        "context": context or "unspecified"
    }
    
    # Log through CertifiedMath if available
    try:
        cm = CertifiedMath()
        cm.log_list.append(log_entry)
    except Exception:
        # If CertifiedMath is not available, we can't log
        pass

def raise_with_logging(exception: Exception, context: Optional[str] = None) -> None:
    """
    Raise an exception after logging it through CertifiedMath.
    
    Args:
        exception: The exception to raise
        context: Additional context information
    """
    log_fatal_exception(exception, context)
    raise exception