"""
Module Interface - Base Contract for All CEE Modules

Zero-Simulation Compliant
"""
from typing import Protocol, Dict, Any, List
from pydantic import BaseModel, Field

class ModuleInput(BaseModel):
    """
    Base input schema for all CEE modules.
    All module inputs must extend this base class.
    """
    tick: int = Field(..., description='Current system tick number', ge=0)
    timestamp: int = Field(..., description='Deterministic timestamp', ge=0)
    signature: bytes = Field(..., description='PQC signature of input')
    prev_hash: str = Field(..., description='Previous entry hash for chain integrity')

    class Config:
        frozen = True
        arbitrary_types_allowed = True

class ModuleOutput(BaseModel):
    """
    Base output schema for all CEE modules.
    All module outputs must extend this base class.
    """
    tick: int = Field(..., description='Tick number for this output', ge=0)
    state_delta: Dict[str, Any] = Field(default_factory=dict, description='State changes')
    audit_log: List[Dict[str, Any]] = Field(default_factory=list, description='Audit entries')
    next_hash: str = Field(..., description='Hash of this output for chain integrity')

    class Config:
        frozen = True
        arbitrary_types_allowed = True

class CEEModule(Protocol):
    """
    Base protocol for all Coherent Economic Engine modules.
    
    Design Principles:
    - Strict isolation: No direct state access between modules
    - Deterministic: Same inputs → same outputs
    - Auditable: All operations logged with PQC signatures
    - Type-safe: Pydantic schemas enforce contracts
    """

    def process(self, input: ModuleInput) -> ModuleOutput:
        """
        Process input and return deterministic output.
        
        Args:
            input: Validated module input
            
        Returns:
            Module output with state delta and audit log
            
        Deterministic Guarantee:
            Same input → same output across all runs and nodes
            
        Raises:
            ValidationError: If input contract is violated
        """
        ...

    def validate_input(self, input: ModuleInput) -> bool:
        """
        Validate input contract before processing.
        
        Args:
            input: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        ...

    def get_audit_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema for this module's audit logs.
        
        Returns:
            JSON schema dict
        """
        ...