"""
QAmount.py - QFS V13 Economic Quantity Type

Canonical economic type for all financial calculations in QFS V13.
Wraps BigNum128 with additional economic semantics and serialization.
"""
from typing import Any, Union
from ..BigNum128 import BigNum128
from ..CertifiedMath import CertifiedMath

class QAmount:
    """
    Economic quantity type for QFS V13.
    
    Wraps BigNum128 with economic semantics and canonical serialization.
    All financial calculations in QFS V13 should use this type.
    """

    def __init__(self, value: Union[BigNum128, int, str, 'QAmount']):
        """
        Initialize a QAmount from various input types.
        
        Args:
            value: The value to initialize from. Can be:
                - BigNum128: Direct wrapping
                - int: Integer value (scaled to fixed-point)
                - str: String representation of decimal number
                - QAmount: Copy constructor
        """
        if isinstance(value, QAmount):
            self._value = value._value.copy()
        elif isinstance(value, BigNum128):
            self._value = value.copy()
        elif isinstance(value, int):
            self._value = BigNum128.from_int(value)
        elif isinstance(value, str):
            self._value = BigNum128.from_string(value)
        else:
            raise TypeError(f'Cannot convert {type(value)} to QAmount')

    @property
    def value(self) -> BigNum128:
        """Get the underlying BigNum128 value."""
        return self._value.copy()

    @classmethod
    def zero(cls) -> 'QAmount':
        """Create a QAmount representing zero."""
        return cls(BigNum128.zero())

    @classmethod
    def one(cls) -> 'QAmount':
        """Create a QAmount representing one."""
        return cls(BigNum128.one())

    def __add__(self, other: Union['QAmount', int, str]) -> 'QAmount':
        """Add two QAmounts or a QAmount and a scalar."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        result_value = self._value + other._value
        return QAmount(result_value)

    def __sub__(self, other: Union['QAmount', int, str]) -> 'QAmount':
        """Subtract two QAmounts or a QAmount and a scalar."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        result_value = self._value - other._value
        return QAmount(result_value)

    def __mul__(self, other: Union['QAmount', int, str]) -> 'QAmount':
        """Multiply two QAmounts or a QAmount and a scalar."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        result_value = self._value * other._value
        return QAmount(result_value)

    def __truediv__(self, other: Union['QAmount', int, str]) -> 'QAmount':
        """Divide two QAmounts or a QAmount and a scalar."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        result_value = self._value // other._value
        return QAmount(result_value)

    def __floordiv__(self, other: Union['QAmount', int, str]) -> 'QAmount':
        """Floor divide two QAmounts or a QAmount and a scalar."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        result_value = self._value // other._value
        return QAmount(result_value)

    def __eq__(self, other: Any) -> bool:
        """Check equality with another QAmount."""
        if not isinstance(other, QAmount):
            return False
        return self._value == other._value

    def __lt__(self, other: Union['QAmount', int, str]) -> bool:
        """Less than comparison."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        return self._value < other._value

    def __le__(self, other: Union['QAmount', int, str]) -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        return self._value <= other._value

    def __gt__(self, other: Union['QAmount', int, str]) -> bool:
        """Greater than comparison."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        return self._value > other._value

    def __ge__(self, other: Union['QAmount', int, str]) -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        return self._value >= other._value

    def __ne__(self, other: Any) -> bool:
        """Not equal comparison."""
        return not self.__eq__(other)

    def __iadd__(self, other: Union['QAmount', int, str]) -> 'QAmount':
        """In-place addition."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        self._value = self._value + other._value
        return self

    def __isub__(self, other: Union['QAmount', int, str]) -> 'QAmount':
        """In-place subtraction."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        self._value = self._value - other._value
        return self

    def __imul__(self, other: Union['QAmount', int, str]) -> 'QAmount':
        """In-place multiplication."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        self._value = self._value * other._value
        return self

    def __itruediv__(self, other: Union['QAmount', int, str]) -> 'QAmount':
        """In-place division."""
        if not isinstance(other, QAmount):
            other = QAmount(other)
        self._value = self._value // other._value
        return self

    def __neg__(self) -> 'QAmount':
        """Negate the QAmount (requires using CertifiedMath for sign handling)."""
        raise NotImplementedError('QAmount is unsigned; use CertifiedMath identities for negation')

    def __pos__(self) -> 'QAmount':
        """Positive (identity)."""
        return QAmount(self)

    def __abs__(self) -> 'QAmount':
        """Absolute value (identity for unsigned)."""
        return QAmount(self)

    def to_canonical_json(self) -> str:
        """
        Serialize to canonical JSON format.
        
        Returns:
            str: Canonical JSON representation
        """
        return self._value.to_decimal_string(fixed_width=True)

    @classmethod
    def from_canonical_json(cls, json_str: str) -> 'QAmount':
        """
        Deserialize from canonical JSON format.
        
        Args:
            json_str: Canonical JSON string representation
            
        Returns:
            QAmount: Deserialized QAmount
        """
        return cls(BigNum128.from_string(json_str))

    def __str__(self) -> str:
        """String representation."""
        return str(self._value)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f'QAmount({self._value.to_decimal_string()})'

    def __hash__(self) -> int:
        """Hash value for use in dictionaries and sets."""
        return hash(self._value)
