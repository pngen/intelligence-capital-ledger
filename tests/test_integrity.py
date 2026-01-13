import unittest
from datetime import datetime
from uuid import uuid4

from icl.core import (
    IntelligenceCapitalLedger,
    IntegrityChecker,
    IntegrityError,
    IntelligenceAsset,
    DepreciationMethod
)


class TestIntegrity(unittest.TestCase):
    def setUp(self):
        self.ledger = IntelligenceCapitalLedger()
        self.checker = IntegrityChecker(self.ledger)

    def test_validate_asset_valid(self):
        asset = IntelligenceAsset(
            asset_id=uuid4(),
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12,
            created_at=datetime.now()
        )

        try:
            self.checker.validate_asset(asset)
        except IntegrityError:
            self.fail("Valid asset should not raise IntegrityError")

    def test_validate_asset_no_owner(self):
        asset = IntelligenceAsset(
            asset_id=uuid4(),
            owner="",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12,
            created_at=datetime.now()
        )

        with self.assertRaises(IntegrityError):
            self.checker.validate_asset(asset)

    def test_validate_asset_negative_value(self):
        asset = IntelligenceAsset(
            asset_id=uuid4(),
            owner="team-alpha",
            initial_value=-1000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12,
            created_at=datetime.now()
        )

        with self.assertRaises(IntegrityError):
            self.checker.validate_asset(asset)

    def test_validate_asset_zero_value(self):
        asset = IntelligenceAsset(
            asset_id=uuid4(),
            owner="team-alpha",
            initial_value=0.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12,
            created_at=datetime.now()
        )

        with self.assertRaises(IntegrityError):
            self.checker.validate_asset(asset)

    def test_validate_asset_negative_useful_life(self):
        asset = IntelligenceAsset(
            asset_id=uuid4(),
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=-12,
            created_at=datetime.now()
        )

        with self.assertRaises(IntegrityError):
            self.checker.validate_asset(asset)

    def test_validate_event_valid(self):
        asset_id = uuid4()
        self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        event = self.ledger.events[0] if self.ledger.events else None

        try:
            self.checker.validate_event(event)
        except IntegrityError:
            self.fail("Valid event should not raise IntegrityError")

    def test_validate_entry_valid(self):
        asset_id = uuid4()
        self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        event = self.ledger.events[0] if self.ledger.events else None

        try:
            self.checker.validate_entry(self.ledger.entries[0])
        except IntegrityError:
            self.fail("Valid entry should not raise IntegrityError")

    def test_check_all_integrity_no_errors(self):
        asset_id = uuid4()
        self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        errors = self.checker.check_all_integrity()
        self.assertEqual(len(errors), 0)

    def test_check_all_integrity_with_errors(self):
        # Create an invalid asset
        asset = IntelligenceAsset(
            asset_id=uuid4(),
            owner="",
            initial_value=-1000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12,
            created_at=datetime.now()
        )
        self.ledger.assets[asset.asset_id] = asset

        errors = self.checker.check_all_integrity()
        self.assertGreater(len(errors), 0)

    def test_validate_depreciation_period_no_overlap(self):
        from icl.core import IntelligenceCapitalLifecycle
        
        asset_id = uuid4()
        ledger = IntelligenceCapitalLedger()
        lifecycle = IntelligenceCapitalLifecycle(ledger)
        
        lifecycle.capitalize(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        # Record first depreciation period
        lifecycle.depreciate(asset_id, datetime(2023, 1, 1), datetime(2023, 6, 30))

        # Test that no overlap is detected when there's none
        try:
            self.checker.validate_depreciation_period(
                asset_id, 
                datetime(2023, 7, 1), 
                datetime(2023, 12, 31)
            )
        except IntegrityError:
            self.fail("Valid period should not raise IntegrityError")
            
    def test_validate_depreciation_period_with_overlap(self):
        from icl.core import IntelligenceCapitalLifecycle
        
        asset_id = uuid4()
        ledger = IntelligenceCapitalLedger()
        lifecycle = IntelligenceCapitalLifecycle(ledger)
        
        lifecycle.capitalize(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )
        
        # Record first depreciation
        lifecycle.depreciate(asset_id, datetime(2023, 1, 1), datetime(2023, 6, 30))
        
        # Try to depreciate overlapping period - should fail
        with self.assertRaises(IntegrityError):
            self.checker.validate_depreciation_period(
                asset_id, 
                datetime(2023, 6, 1),  # Overlaps with previous period
                datetime(2023, 12, 31)
            )


if __name__ == '__main__':
    unittest.main()