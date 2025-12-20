"""
Quantum operation models for the ATLAS API.
"""

from v13.libs.economics.QAmount import QAmount
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator, ConfigDict


class QuantumKeyPair(BaseModel):
    """Model representing a quantum-resistant key pair."""

    key_id: str = Field(..., description="Unique key pair identifier")
    name: str = Field(..., description="User-defined name for the key pair")
    public_key: str = Field(..., description="Public key in hex format")
    algorithm: str = Field(..., description="Algorithm used for key generation")
    created_at: Optional[str] = Field(
        None, description="Creation timestamp in ISO format"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional key metadata"
    )


class QuantumSignature(BaseModel):
    """Model representing a quantum-resistant signature."""

    key_id: str = Field(..., description="ID of the key used for signing")
    public_key: str = Field(..., description="Public key in hex format")
    signature: str = Field(..., description="Digital signature in hex format")
    algorithm: str = Field(..., description="Signature algorithm")
    timestamp: Optional[str] = Field(
        None, description="Signature timestamp in ISO format"
    )


class QuantumSignatureVerify(BaseModel):
    """Model for verifying a quantum signature."""

    data: str = Field(..., description="The original data that was signed")
    signature: str = Field(..., description="The signature to verify")
    public_key: str = Field(..., description="Public key for verification")
    algorithm: Optional[str] = Field(
        "QFS-QUANTUM-256", description="Signature algorithm (default: QFS-QUANTUM-256)"
    )


class EntangledPair(BaseModel):
    """Model representing a pair of entangled quantum states."""

    state1: str = Field(..., description="First entangled state (hex)")
    state2: str = Field(..., description="Second entangled state (hex)")
    created_at: Optional[str] = Field(
        None, description="Creation timestamp in ISO format"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional entanglement metadata"
    )


class QuantumState(BaseModel):
    """Model representing a quantum state measurement result."""

    original_state: str = Field(..., description="Original quantum state (hex)")
    collapsed_state: str = Field(..., description="State after measurement (hex)")
    measurement_result: bool = Field(..., description="Measurement result (0 or 1)")
    basis_used: int = Field(..., description="Measurement basis used (0 or 1)")
    timestamp: Optional[str] = Field(
        None, description="Measurement timestamp in ISO format"
    )


class QuantumCircuitRequest(BaseModel):
    """Model for submitting a custom quantum circuit."""

    qubits: int = Field(..., ge=1, le=100, description="Number of qubits")
    gates: List[Dict[str, Any]] = Field(
        ..., description="List of quantum gates to apply"
    )
    measurements: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of measurements to perform"
    )
    shots: int = Field(
        1024, ge=1, le=10000, description="Number of measurement shots to perform"
    )


class QuantumCircuitResult(BaseModel):
    """Model representing the result of a quantum circuit execution."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    circuit_id: str = Field(..., description="Unique circuit execution ID")
    counts: Dict[str, int] = Field(
        ..., description="Measurement results with their counts"
    )
    execution_time: QAmount = Field(..., description="Execution time in seconds")
    backend: str = Field("simulator", description="Quantum backend used for execution")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional execution metadata"
    )


class QuantumRandomRequest(BaseModel):
    """Model for requesting quantum random numbers."""

    count: int = Field(
        1, ge=1, le=1000, description="Number of random numbers to generate"
    )
    min_value: int = Field(0, description="Minimum value (inclusive)")
    max_value: int = Field(2**32 - 1, description="Maximum value (inclusive)")

    @validator("max_value")
    def validate_range(cls, v, values):
        if "min_value" in values and v <= values["min_value"]:
            raise ValueError("max_value must be greater than min_value")
        return v


class QuantumRandomResponse(BaseModel):
    """Model for quantum random number generation response."""

    random_numbers: List[int] = Field(
        ..., description="List of generated random numbers"
    )
    min_value: int = Field(..., description="Minimum value (inclusive)")
    max_value: int = Field(..., description="Maximum value (inclusive)")
    generated_at: str = Field(..., description="Generation timestamp in ISO format")

