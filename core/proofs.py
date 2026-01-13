from typing import Dict, List, Optional
from uuid import UUID

from .types import CapitalProof, IntelligenceAsset, CapitalEvent, LedgerEntry


class CapitalProofGenerator:
    """Generates capital proofs for auditability."""

    def __init__(self, ledger):
        self.ledger = ledger

    def generate_asset_proof(self, asset_id: UUID) -> CapitalProof:
        """Generate a proof of an asset's existence and properties."""
        asset = self.ledger.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Unknown asset {asset_id}")

        return self.ledger.generate_proof(asset_id)

    def generate_execution_proof(
        self,
        asset_id: UUID,
        event_id: Optional[UUID] = None
    ) -> CapitalProof:
        """Generate a proof linking execution to capital."""
        # This would typically involve cross-referencing with ICAE data
        return self.ledger.generate_proof(asset_id, event_id)

    def generate_financial_outcome_proof(
        self,
        asset_id: UUID,
        start_date: str,
        end_date: str
    ) -> CapitalProof:
        """Generate a proof linking capital to financial outcomes."""
        # This would involve mapping to financial reporting systems
        return self.ledger.generate_proof(asset_id)

    def reconstruct_proof(self, proof_id: UUID) -> Optional[CapitalProof]:
        """Reconstruct a proof from its ID."""
        for proof in self.ledger.proofs:
            if proof.proof_id == proof_id:
                return proof
        return None

    def get_asset_history(self, asset_id: UUID) -> List[Dict]:
        """Get the complete history of an asset."""
        events = self.ledger.get_events_for_asset(asset_id)
        entries = self.ledger.get_entries_for_asset(asset_id)

        # Fix: Use event.event_id instead of comparing to itself
        return [
            {
                "event": e,
                "entries": [entry for entry in entries if entry.event_id == e.event_id]
            }
            for e in events
        ]