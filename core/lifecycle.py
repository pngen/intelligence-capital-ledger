from datetime import datetime
from uuid import UUID, uuid4

from .types import (
    IntelligenceAsset,
    CapitalEvent,
    AssetStatus,
    DepreciationMethod,
    JournalEntry,
    AccountType
)
from .ledger import IntelligenceCapitalLedger
from .depreciation import calculate_depreciation


class IntelligenceCapitalLifecycle:
    """Manages the full lifecycle of intelligence assets."""

    def __init__(self, ledger: IntelligenceCapitalLedger):
        self.ledger = ledger

    def capitalize(
        self,
        asset_id: UUID,
        owner: str,
        initial_value: float,
        depreciation_method: DepreciationMethod,
        useful_life_months: int
    ) -> IntelligenceAsset:
        """Capitalize a new intelligence asset."""
        asset = self.ledger.create_asset(
            asset_id=asset_id,
            owner=owner,
            initial_value=initial_value,
            depreciation_method=depreciation_method,
            useful_life_months=useful_life_months
        )
        
        # Record double-entry for capitalization
        # Debit Asset, Credit Cash/Equity
        journal_entry = JournalEntry(
            entry_id=uuid4(),
            event_id=uuid4(),  # Create a new event ID for this transaction
            timestamp=datetime.now(),
            debit_account=AccountType.ASSET,
            credit_account=AccountType.ACCUMULATED_DEPRECIATION,  # Simplified - in practice would be cash or equity
            amount=initial_value,
            description="Asset capitalization",
            metadata={
                "asset_id": str(asset_id),
                "owner": owner,
                "initial_value": initial_value
            }
        )
        self.ledger.record_journal_entry(journal_entry)
        
        return asset

    def allocate(self, asset_id: UUID, target_owner: str) -> CapitalEvent:
        """Allocate an asset to a new owner."""
        asset = self.ledger.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Unknown asset {asset_id}")

        # Save old owner BEFORE updating
        old_owner = asset.owner
        asset.owner = target_owner

        event = CapitalEvent(
            event_id=uuid4(),
            asset_id=asset_id,
            event_type="allocation",
            timestamp=datetime.now(),
            details={
                "from_owner": old_owner,  # Use saved old owner
                "to_owner": target_owner
            }
        )
        self.ledger.record_event(event)
        return event

    def utilize(self, asset_id: UUID, amount: float) -> CapitalEvent:
        """Record utilization of an intelligence asset."""
        event = CapitalEvent(
            event_id=uuid4(),
            asset_id=asset_id,
            event_type="utilization",
            timestamp=datetime.now(),
            details={"amount": amount}
        )
        self.ledger.record_event(event)
        return event

    def depreciate(self, asset_id: UUID, start_date: datetime, end_date: datetime, 
                   salvage_value: float = 0.0, rate_multiplier: float = 2.0) -> CapitalEvent:
        """Apply depreciation to an asset."""
        asset = self.ledger.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Unknown asset {asset_id}")

        # Validate depreciation period
        from .integrity import IntegrityChecker
        checker = IntegrityChecker(self.ledger)
        checker.validate_depreciation_period(asset_id, start_date, end_date)

        depreciation_amount, new_value = calculate_depreciation(
            asset, start_date, end_date, salvage_value, rate_multiplier
        )

        # Update asset value
        previous_value = asset.current_value
        asset.current_value = new_value

        event = CapitalEvent(
            event_id=uuid4(),
            asset_id=asset_id,
            event_type="depreciation",
            timestamp=datetime.now(),
            details={
                "amount": depreciation_amount,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "salvage_value": salvage_value,
                "rate_multiplier": rate_multiplier
            }
        )
        self.ledger.record_event(event)
        
        # Record double-entry journal entries for depreciation
        if depreciation_amount > 0:
            # Debit Depreciation Expense, Credit Accumulated Depreciation
            journal_entry = JournalEntry(
                entry_id=uuid4(),
                event_id=event.event_id,
                timestamp=datetime.now(),
                debit_account=AccountType.DEPRECIATION_EXPENSE,
                credit_account=AccountType.ACCUMULATED_DEPRECIATION,
                amount=depreciation_amount,
                description="Asset depreciation",
                metadata={
                    "asset_id": str(asset_id),
                    "previous_value": previous_value,
                    "new_value": asset.current_value,
                    **event.details
                }
            )
            self.ledger.record_journal_entry(journal_entry)
        
        return event

    def retire(self, asset_id: UUID) -> CapitalEvent:
        """Retire an intelligence asset."""
        asset = self.ledger.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Unknown asset {asset_id}")

        # Mark as retired
        asset.status = AssetStatus.RETIRED

        event = CapitalEvent(
            event_id=uuid4(),
            asset_id=asset_id,
            event_type="retirement",
            timestamp=datetime.now(),
            details={}
        )
        self.ledger.record_event(event)
        
        # Record journal entry for retirement (write-off)
        if asset.current_value and asset.current_value > 0:
            journal_entry = JournalEntry(
                entry_id=uuid4(),
                event_id=event.event_id,
                timestamp=datetime.now(),
                debit_account=AccountType.ACCUMULATED_DEPRECIATION,
                credit_account=AccountType.ASSET,
                amount=asset.current_value,
                description="Asset retirement write-off",
                metadata={
                    "asset_id": str(asset_id),
                    "retired_value": asset.current_value
                }
            )
            self.ledger.record_journal_entry(journal_entry)
        
        return event