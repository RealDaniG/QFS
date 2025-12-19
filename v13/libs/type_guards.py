"""
Type Guards and Safety Utilities
Provides robust type checking and conversion for QFS/ATLAS
"""

from typing import (
    Union,
    TypeVar,
    Dict,
    Any,
    List,
    Protocol,
    runtime_checkable,
    Optional,
)
from enum import Enum
from v13.libs.BigNum128 import BigNum128

T = TypeVar("T")


@runtime_checkable
class DeterministicNumeric(Protocol):
    """Protocol for types that support deterministic fixed-point arithmetic"""

    value: int

    def add(self, other: "DeterministicNumeric") -> "DeterministicNumeric": ...
    def sub(self, other: "DeterministicNumeric") -> "DeterministicNumeric": ...
    def mul(self, other: "DeterministicNumeric") -> "DeterministicNumeric": ...
    def div(self, other: "DeterministicNumeric") -> "DeterministicNumeric": ...
    def to_decimal_string(self, fixed_width: bool = True) -> str: ...


@runtime_checkable
class EconomicValidatable(Protocol):
    """Protocol for objects that can be validated by EconomicsGuard"""

    def to_dict(self) -> Dict[str, Any]: ...


@runtime_checkable
class AuditLogged(Protocol):
    """Protocol for operations that must be recorded in the canonical audit list"""

    def _log_operation(
        self,
        op_name: str,
        inputs: Dict[str, Any],
        result: Any,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
    ) -> None: ...


def ensure_bignum(value: Union[BigNum128, int, str]) -> BigNum128:
    """Safely convert any numeric type to BigNum128"""
    if isinstance(value, BigNum128):
        return value
    elif isinstance(value, int):
        return BigNum128.from_int(value)
    elif isinstance(value, str):
        return BigNum128.from_string(value)
    else:
        raise TypeError(f"Cannot convert {type(value)} to BigNum128")


def ensure_int(value: Union[int, BigNum128]) -> int:
    """Extract integer from BigNum128 or pass through int"""
    if isinstance(value, int):
        return value
    elif isinstance(value, BigNum128):
        return value.value
    else:
        raise TypeError(f"Cannot convert {type(value)} to int")


def validate_event_schema(event: dict) -> bool:
    """Validate event has required fields"""
    required = ["event_type", "timestamp", "wallet_id", "amount"]
    return all(key in event for key in required)


def safe_enum_serialize(enum_value: Union[Enum, str, Any]) -> str:
    """Safely serialize Enum to string"""
    if isinstance(enum_value, Enum):
        return str(enum_value.value)
    elif isinstance(enum_value, str):
        return enum_value
    else:
        # Fallback using getattr if it mocks an enum or has value attr
        if hasattr(enum_value, "value"):
            return str(enum_value.value)
        raise TypeError(f"Cannot serialize {type(enum_value)} to string")
