from typing import List, Optional
from uuid import UUID, uuid4
from collections import defaultdict
from datetime import datetime

from .types import (
    IntelligenceAsset,
    CapitalEvent,
    LedgerEntry,
    CapitalProof,
    AssetStatus,
    DepreciationMethod,
    JournalEntry,
    AccountType
)


class IntelligenceCapitalLedger:
    """Main ledger for tracking intelligence capital assets and events."""

    def __init__(self):
        self.assets: dict[UUID, IntelligenceAsset] = {}
        self.events: list[CapitalEvent] = []
        self.entries: list[LedgerEntry] = []
        self.journal_entries: list[JournalEntry] = []
        self.proofs: list[CapitalProof] = []
        
        # Add indexes for performance
        self._events_by_asset: dict[UUID, list[CapitalEvent]] = defaultdict(list)
        self._entries_by_asset: dict[UUID, list[LedgerEntry]] = defaultdict(list)
        self._journal_entries_by_asset: dict[UUID, list[JournalEntry]] = defaultdict(list)

    def create_asset(
        self,
        asset_id: UUID,
        owner: str,
        initial_value: float,
        depreciation_method: DepreciationMethod,
        useful_life_months: int
    ) -> IntelligenceAsset:
        """Create a new intelligence asset."""
        if asset_id in self.assets:
            raise ValueError(f"Asset with ID {asset_id} already exists")

        asset = IntelligenceAsset(
            asset_id=asset_id,
            owner=owner,
            initial_value=initial_value,
            depreciation_method=depreciation_method,
            useful_life_months=useful_life_months,
            created_at=datetime.now(),
            current_value=initial_value
        )
        self.assets[asset_id] = asset
        return asset

    def record_event(self, event: CapitalEvent) -> None:
        """Record a capital event and generate corresponding ledger entries."""
        if event.asset_id not in self.assets:
            raise ValueError(f"Unknown asset {event.asset_id}")

        self.events.append(event)
        self._events_by_asset[event.asset_id].append(event)  # Index

        # Generate ledger entries based on event type
        entry = LedgerEntry(
            entry_id=uuid4(),
            event_id=event.event_id,
            asset_id=event.asset_id,
            timestamp=event.timestamp,
            amount=event.details.get("amount", 0.0),
            description=event.event_type,
            metadata=event.details
        )
        self.entries.append(entry)
        self._entries_by_asset[event.asset_id].append(entry)  # Index

    def record_journal_entry(self, journal_entry: JournalEntry) -> None:
        """Record a double-entry journal entry."""
        self.journal_entries.append(journal_entry)
        self._journal_entries_by_asset[journal_entry.event_id].append(journal_entry)

    def generate_proof(self, asset_id: UUID, event_id: Optional[UUID] = None) -> CapitalProof:
        """Generate a capital proof for an asset or specific event."""
        if asset_id not in self.assets:
            raise ValueError(f"Unknown asset {asset_id}")

        # Get the last proof for this asset to create chain
        asset_proofs = [p for p in self.proofs if p.asset_id == asset_id]
        previous_hash = asset_proofs[-1].proof_hash if asset_proofs else None

        asset = self.assets[asset_id]
        proof = CapitalProof(
            proof_id=uuid4(),
            asset_id=asset_id,
            event_id=event_id,
            timestamp=datetime.now(),
            origin="ICL",
            previous_proof_hash=previous_hash,  # Link to previous
            content={
                "asset_id": str(asset.asset_id),
                "owner": asset.owner,
                "initial_value": asset.initial_value,
                "depreciation_method": asset.depreciation_method.value,
                "useful_life_months": asset.useful_life_months,
                "status": asset.status.value,
                "current_value": asset.current_value
            }
        )
        proof.proof_hash = proof.compute_hash()
        self.proofs.append(proof)
        return proof

    def get_asset(self, asset_id: UUID) -> Optional[IntelligenceAsset]:
        """Retrieve an intelligence asset by ID."""
        return self.assets.get(asset_id)

    def get_events_for_asset(self, asset_id: UUID) -> List[CapitalEvent]:
        """Get all events associated with an asset."""
        return self._events_by_asset[asset_id]

    def get_entries_for_asset(self, asset_id: UUID) -> List[LedgerEntry]:
        """Get all ledger entries associated with an asset."""
        return self._entries_by_asset[asset_id]
    
    def get_journal_entries_for_asset(self, asset_id: UUID) -> List[JournalEntry]:
        """Get all journal entries associated with an asset."""
        # Get all journal entries for events related to this asset
        asset_events = self.get_events_for_asset(asset_id)
        event_ids = {e.event_id for e in asset_events}
        
        return [
            entry for entry in self.journal_entries 
            if entry.event_id in event_ids
        ]
    
    def verify_journal_balance(self) -> bool:
        """Verify that all journal entries are valid (positive amounts)."""
        # In current implementation, each JournalEntry represents a complete debit/credit pair
        # with the same amount. So we just check that amounts are positive.
        return all(entry.amount > 0 for entry in self.journal_entries)
    
    def export_audit_trail(self, format: str = "json") -> str:
        """Export complete audit trail in specified format."""
        import json
        from dataclasses import asdict
        
        if format == "json":
            return json.dumps({
                "assets": [asdict(a) for a in self.assets.values()],
                "events": [asdict(e) for e in self.events],
                "entries": [asdict(e) for e in self.entries],
                "journal_entries": [asdict(j) for j in self.journal_entries],
                "proofs": [asdict(p) for p in self.proofs]
            }, default=str, indent=2)
        elif format == "csv":
            # Simple CSV export - in practice would be more complex
            return "CSV export not implemented"