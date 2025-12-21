from typing import List, Dict, Any, Optional
from v18.consensus.interfaces import IConsensusLog


class InMemoryConsensusLog(IConsensusLog):
    """In-memory implementation of IConsensusLog for testing and prototyping."""

    def __init__(self):
        # Index 0 is often reserved or a sentinel in Raft, but we'll use 1-based indexing for entries.
        self.entries: List[Dict[str, Any]] = []

    def append(self, entry: Dict[str, Any]) -> int:
        """Append entry and return its index."""
        self.entries.append(entry)
        return len(self.entries)

    def get_entries(
        self, start_index: int, end_index: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve entries from log (1-based index)."""
        if start_index < 1:
            start_index = 1

        # Adjust for 0-based list
        list_start = start_index - 1
        if end_index is None:
            return self.entries[list_start:]

        list_end = end_index
        return self.entries[list_start:list_end]

    def last_index(self) -> int:
        """Get the index of the last entry."""
        return len(self.entries)

    def last_term(self) -> int:
        """Get the term of the last entry."""
        if not self.entries:
            return 0
        return self.entries[-1]["term"]
