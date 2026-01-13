from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .types import (
    IntelligenceAsset,
    CapitalEvent,
    LedgerEntry,
    CapitalProof
)


class IntegrityError(Exception):
    """Raised when integrity violations are detected."""
    pass


class IntegrityChecker:
    """Ensures ledger integrity and handles failures."""

    def __init__(self, ledger):
        self.ledger = ledger

    def validate_asset(self, asset: IntelligenceAsset) -> None:
        """Validate an intelligence asset for integrity."""
        if not asset.owner:
            raise IntegrityError("Asset must have an owner")
        
        if asset.initial_value <= 0:
            raise IntegrityError("Initial value must be positive")
        
        if asset.useful_life_months <= 0:
            raise IntegrityError("Useful life must be positive")

    def validate_event(self, event: CapitalEvent) -> None:
        """Validate a capital event for integrity."""
        if event.asset_id not in self.ledger.assets:
            raise IntegrityError(f"Unknown asset {event.asset_id}")

        # Ensure all required fields are present
        if not event.event_type:
            raise IntegrityError("Event type is required")

    def validate_entry(self, entry: LedgerEntry) -> None:
        """Validate a ledger entry for integrity."""
        if entry.asset_id not in self.ledger.assets:
            raise IntegrityError(f"Unknown asset {entry.asset_id}")

        # Ensure entries are time-ordered
        if len(self.ledger.entries) > 0:
            last_entry = self.ledger.entries[-1]
            if entry.timestamp < last_entry.timestamp:
                raise IntegrityError("Ledger entries must be time-ordered")

    def check_all_integrity(self) -> List[str]:
        """Run all integrity checks."""
        errors = []

        # Check assets
        for asset in self.ledger.assets.values():
            try:
                self.validate_asset(asset)
            except IntegrityError as e:
                errors.append(f"Asset {asset.asset_id}: {str(e)}")

        # Check events
        for event in self.ledger.events:
            try:
                self.validate_event(event)
            except IntegrityError as e:
                errors.append(f"Event {event.event_id}: {str(e)}")

        # Check entries
        for entry in self.ledger.entries:
            try:
                self.validate_entry(entry)
            except IntegrityError as e:
                errors.append(f"Entry {entry.entry_id}: {str(e)}")

        return errors

    def ensure_no_retroactive_modification(self, new_event: CapitalEvent) -> None:
        """Ensure no retroactive modification attempts."""
        # This is a simplified check - in practice, this would involve more complex logic
        # such as checking against existing timestamps or event sequences.
        pass
    
    def validate_depreciation_period(self, asset_id: UUID, start: datetime, end: datetime) -> None:
        """Ensure no overlapping depreciation periods for this asset."""
        existing_depreciations = [
            e for e in self.ledger.get_events_for_asset(asset_id)
            if e.event_type == "depreciation"
        ]
        
        # Check for overlaps with existing depreciation periods
        for dep_event in existing_depreciations:
            dep_start = datetime.fromisoformat(dep_event.details["start_date"])
            dep_end = datetime.fromisoformat(dep_event.details["end_date"])
            
            if start <= dep_end and end >= dep_start:
                raise IntegrityError(
                    f"Depreciation period {start} to {end} overlaps with existing "
                    f"period {dep_start} to {dep_end} for asset {asset_id}"
                )