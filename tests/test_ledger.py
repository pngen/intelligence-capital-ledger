import unittest
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from icl.core import (
    IntelligenceCapitalLedger,
    IntelligenceAsset,
    CapitalEvent,
    AssetStatus,
    DepreciationMethod
)


class TestIntelligenceCapitalLedger(unittest.TestCase):
    def setUp(self):
        self.ledger = IntelligenceCapitalLedger()

    def test_create_asset(self):
        asset_id = uuid4()
        asset = self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        self.assertEqual(asset.asset_id, asset_id)
        self.assertEqual(asset.owner, "team-alpha")
        self.assertEqual(asset.initial_value, 10000.0)
        self.assertEqual(asset.depreciation_method, DepreciationMethod.LINEAR)
        self.assertEqual(asset.useful_life_months, 12)
        self.assertEqual(asset.status, AssetStatus.ACTIVE)
        self.assertEqual(asset.current_value, 10000.0)

    def test_create_duplicate_asset(self):
        asset_id = uuid4()
        self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        with self.assertRaises(ValueError):
            self.ledger.create_asset(
                asset_id=asset_id,
                owner="team-beta",
                initial_value=5000.0,
                depreciation_method=DepreciationMethod.LINEAR,
                useful_life_months=12
            )

    def test_record_event(self):
        asset_id = uuid4()
        self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        event = CapitalEvent(
            event_id=uuid4(),
            asset_id=asset_id,
            event_type="utilization",
            timestamp=datetime.now(),
            details={"amount": 500.0}
        )

        self.ledger.record_event(event)

        self.assertEqual(len(self.ledger.events), 1)
        self.assertEqual(len(self.ledger.entries), 1)

    def test_get_asset(self):
        asset_id = uuid4()
        asset = self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        retrieved_asset = self.ledger.get_asset(asset_id)
        self.assertEqual(retrieved_asset, asset)

    def test_get_nonexistent_asset(self):
        asset = self.ledger.get_asset(uuid4())
        self.assertIsNone(asset)

    def test_get_events_for_asset(self):
        asset_id = uuid4()
        self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        event1 = CapitalEvent(
            event_id=uuid4(),
            asset_id=asset_id,
            event_type="utilization",
            timestamp=datetime.now(),
            details={"amount": 500.0}
        )

        event2 = CapitalEvent(
            event_id=uuid4(),
            asset_id=asset_id,
            event_type="allocation",
            timestamp=datetime.now(),
            details={"from_owner": "team-alpha", "to_owner": "team-beta"}
        )

        self.ledger.record_event(event1)
        self.ledger.record_event(event2)

        events = self.ledger.get_events_for_asset(asset_id)
        self.assertEqual(len(events), 2)

    def test_get_entries_for_asset(self):
        asset_id = uuid4()
        self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        event1 = CapitalEvent(
            event_id=uuid4(),
            asset_id=asset_id,
            event_type="utilization",
            timestamp=datetime.now(),
            details={"amount": 500.0}
        )

        event2 = CapitalEvent(
            event_id=uuid4(),
            asset_id=asset_id,
            event_type="allocation",
            timestamp=datetime.now(),
            details={"from_owner": "team-alpha", "to_owner": "team-beta"}
        )

        self.ledger.record_event(event1)
        self.ledger.record_event(event2)

        entries = self.ledger.get_entries_for_asset(asset_id)
        self.assertEqual(len(entries), 2)
        
    def test_verify_journal_balance(self):
        # Create a ledger with balanced journal entries
        ledger = IntelligenceCapitalLedger()
        
        # Create an asset and record some events that should balance
        asset_id = uuid4()
        ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )
        
        # Verify balance is initially true (no entries)
        self.assertTrue(ledger.verify_journal_balance())
        
    def test_export_audit_trail(self):
        ledger = IntelligenceCapitalLedger()
        asset_id = uuid4()
        ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )
        
        # Test JSON export
        json_export = ledger.export_audit_trail("json")
        self.assertIsInstance(json_export, str)
        self.assertTrue(len(json_export) > 0)
        
        # Test CSV export (should return empty string for now)
        csv_export = ledger.export_audit_trail("csv")
        self.assertIsInstance(csv_export, str)


if __name__ == '__main__':
    unittest.main()