import unittest
from datetime import datetime, timedelta
from uuid import uuid4

from icl.core import (
    IntelligenceAsset,
    DepreciationMethod,
    calculate_depreciation
)


class TestDepreciation(unittest.TestCase):
    def test_linear_depreciation(self):
        asset = IntelligenceAsset(
            asset_id=uuid4(),
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12,
            created_at=datetime.now()
        )

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 6, 1)

        depreciation_amount, new_value = calculate_depreciation(asset, start_date, end_date)

        # 6 months of linear depreciation on $10k over 12 months
        expected_depreciation = 10000.0 * (6 / 12)
        self.assertAlmostEqual(depreciation_amount, expected_depreciation)
        self.assertAlmostEqual(new_value, 5000.0)

    def test_declining_balance_depreciation(self):
        asset = IntelligenceAsset(
            asset_id=uuid4(),
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.DECLINING_BALANCE,
            useful_life_months=12,
            created_at=datetime.now()
        )

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 6, 1)

        depreciation_amount, new_value = calculate_depreciation(asset, start_date, end_date)

        # Should be more than linear due to declining balance
        self.assertGreater(depreciation_amount, 5000.0)  # Linear would be $5000
        self.assertLess(new_value, 5000.0)  # Value should be less than half

    def test_zero_months(self):
        asset = IntelligenceAsset(
            asset_id=uuid4(),
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12,
            created_at=datetime.now()
        )

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 1)

        depreciation_amount, new_value = calculate_depreciation(asset, start_date, end_date)

        self.assertEqual(depreciation_amount, 0.0)
        self.assertEqual(new_value, 10000.0)

    def test_negative_months(self):
        asset = IntelligenceAsset(
            asset_id=uuid4(),
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12,
            created_at=datetime.now()
        )

        start_date = datetime(2023, 6, 1)
        end_date = datetime(2023, 1, 1)

        depreciation_amount, new_value = calculate_depreciation(asset, start_date, end_date)

        self.assertEqual(depreciation_amount, 0.0)
        self.assertEqual(new_value, 10000.0)

    def test_linear_with_salvage_value(self):
        asset = IntelligenceAsset(
            asset_id=uuid4(),
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12,
            created_at=datetime.now()
        )

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 6, 1)

        depreciation_amount, new_value = calculate_depreciation(asset, start_date, end_date, salvage_value=1000.0)

        # 6 months of linear depreciation on $9k (after salvage) over 12 months
        expected_depreciation = 9000.0 * (6 / 12)
        self.assertAlmostEqual(depreciation_amount, expected_depreciation)
        self.assertAlmostEqual(new_value, 1000.0 + expected_depreciation)

    def test_declining_balance_with_salvage_value(self):
        asset = IntelligenceAsset(
            asset_id=uuid4(),
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.DECLINING_BALANCE,
            useful_life_months=12,
            created_at=datetime.now()
        )

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 6, 1)

        depreciation_amount, new_value = calculate_depreciation(asset, start_date, end_date, salvage_value=1000.0)

        # Should be more than linear due to declining balance
        self.assertGreater(depreciation_amount, 0.0)
        self.assertLess(new_value, 10000.0)  # Value should be less than initial


if __name__ == '__main__':
    unittest.main()