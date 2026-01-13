import unittest
from datetime import datetime
from uuid import UUID, uuid4

from icl.core import (
    IntelligenceCapitalLedger,
    IntelligenceCapitalLifecycle,
    IntelligenceAsset,
    CapitalEvent,
    AssetStatus,
    DepreciationMethod
)


class TestIntelligenceCapitalLifecycle(unittest.TestCase):
    def setUp(self):
        self.ledger = IntelligenceCapitalLedger()
        self.lifecycle = IntelligenceCapitalLifecycle(self.ledger)

    def test_capitalize(self):
        asset_id = uuid4()
        asset = self.lifecycle.capitalize(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        self.assertEqual(asset.asset_id, asset_id)
        self.assertEqual(asset.owner, "team-alpha")
        self.assertEqual(asset.initial_value, 10000.0)
        self.assertEqual(asset.status, AssetStatus.ACTIVE)

    def test_allocate(self):
        asset_id = uuid4()
        self.lifecycle.capitalize(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        event = self.lifecycle.allocate(asset_id, "team-beta")

        # Verify that the asset's owner was updated
        asset = self.ledger.get_asset(asset_id)
        self.assertEqual(asset.owner, "team-beta")
        
        self.assertEqual(event.event_type, "allocation")
        self.assertEqual(event.details["from_owner"], "team-alpha")
        self.assertEqual(event.details["to_owner"], "team-beta")

    def test_utilize(self):
        asset_id = uuid4()
        self.lifecycle.capitalize(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        event = self.lifecycle.utilize(asset_id, 500.0)

        self.assertEqual(event.event_type, "utilization")
        self.assertEqual(event.details["amount"], 500.0)

    def test_depreciate(self):
        asset_id = uuid4()
        self.lifecycle.capitalize(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 6, 1)

        event = self.lifecycle.depreciate(asset_id, start_date, end_date)

        self.assertEqual(event.event_type, "depreciation")
        self.assertIn("amount", event.details)
        self.assertIn("start_date", event.details)
        self.assertIn("end_date", event.details)

    def test_retire(self):
        asset_id = uuid4()
        self.lifecycle.capitalize(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        event = self.lifecycle.retire(asset_id)

        self.assertEqual(event.event_type, "retirement")
        asset = self.ledger.get_asset(asset_id)
        self.assertEqual(asset.status, AssetStatus.RETIRED)
        
    def test_journal_entries_created(self):
        # Test that journal entries are created for all lifecycle events
        asset_id = uuid4()
        self.lifecycle.capitalize(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )
        
        # Check that capitalization created journal entries
        journal_entries = self.ledger.get_journal_entries_for_asset(asset_id)
        self.assertGreater(len(journal_entries), 0)
        
        # Test depreciation creates journal entries
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 6, 1)
        self.lifecycle.depreciate(asset_id, start_date, end_date)
        
        # Should have more journal entries now
        journal_entries_after = self.ledger.get_journal_entries_for_asset(asset_id)
        self.assertGreater(len(journal_entries_after), len(journal_entries))


if __name__ == '__main__':
    unittest.main()