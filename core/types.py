from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID


class AssetStatus(str, Enum):
    ACTIVE = "active"
    DEPRECIATED = "depreciated"
    RETIRED = "retired"


class DepreciationMethod(str, Enum):
    LINEAR = "linear"
    DECLINING_BALANCE = "declining_balance"


class AccountType(str, Enum):
    ASSET = "asset"
    ACCUMULATED_DEPRECIATION = "accumulated_depreciation"
    DEPRECIATION_EXPENSE = "depreciation_expense"


@dataclass
class IntelligenceAsset:
    """A capitalized unit of intelligence capability."""
    asset_id: UUID
    owner: str  # Business unit or mandate identifier
    initial_value: float
    depreciation_method: DepreciationMethod
    useful_life_months: int
    created_at: datetime
    status: AssetStatus = AssetStatus.ACTIVE
    current_value: Optional[float] = None


@dataclass
class CapitalEvent:
    """A discrete economic action involving intelligence capital."""
    event_id: UUID
    asset_id: UUID
    event_type: str  # e.g., "allocation", "utilization", "depreciation"
    timestamp: datetime
    details: Dict[str, Union[str, float, int]]


@dataclass
class LedgerEntry:
    """An immutable, auditable economic record."""
    entry_id: UUID
    event_id: UUID
    asset_id: UUID
    timestamp: datetime
    amount: float
    description: str
    metadata: Dict[str, Union[str, int, float]]


@dataclass
class JournalEntry:
    """A double-entry accounting journal entry."""
    entry_id: UUID
    event_id: UUID
    timestamp: datetime
    debit_account: AccountType
    credit_account: AccountType
    amount: float
    description: str
    metadata: Dict[str, Union[str, int, float]]


@dataclass
class CapitalProof:
    """A machine-verifiable explanation of how a financial figure was derived."""
    proof_id: UUID
    asset_id: UUID
    event_id: Optional[UUID]
    timestamp: datetime
    origin: str  # Source of the proof (e.g., "ICAE", "financial_system")
    content: Dict[str, Union[str, float, int]]
    previous_proof_hash: Optional[str] = None
    proof_hash: Optional[str] = None
    
    def compute_hash(self) -> str:
        """Generate tamper-evident hash of proof content."""
        import json
        content_str = json.dumps(self.content, sort_keys=True)
        hash_input = f"{self.proof_id}{self.timestamp}{content_str}{self.previous_proof_hash or ''}"
        import hashlib
        return hashlib.sha256(hash_input.encode()).hexdigest()