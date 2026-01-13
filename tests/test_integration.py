import unittest
from uuid import UUID, uuid4

from icl.core import IntegrationAdapter, ICAEAttribution
from datetime import datetime


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.adapter = IntegrationAdapter()

    def test_consume_icae_attribution(self):
        attribution_data = {
            "asset_1": {"inference_cost": 1000.0, "execution_time": 3600},
            "asset_2": {"inference_cost": 2000.0, "execution_time": 7200}
        }

        self.adapter.consume_icae_attribution(attribution_data)

        self.assertEqual(self.adapter.icae_data, attribution_data)

    def test_validate_attribution_exists(self):
        asset_id = str(uuid4())
        attribution_data = {
            asset_id: {"inference_cost": 1000.0, "execution_time": 3600}
        }
        self.adapter.consume_icae_attribution(attribution_data)

        result = self.adapter.validate_attribution(UUID(asset_id), {})
        self.assertTrue(result)

    def test_validate_attribution_missing(self):
        asset_id = str(uuid4())
        attribution_data = {
            "other_asset": {"inference_cost": 1000.0, "execution_time": 3600}
        }
        self.adapter.consume_icae_attribution(attribution_data)

        result = self.adapter.validate_attribution(UUID(asset_id), {})
        self.assertFalse(result)

    def test_get_execution_attribution(self):
        asset_id = str(uuid4())
        attribution_data = {
            asset_id: {"inference_cost": 1000.0, "execution_time": 3600}
        }
        self.adapter.consume_icae_attribution(attribution_data)

        result = self.adapter.get_execution_attribution(UUID(asset_id))
        self.assertEqual(result, {"inference_cost": 1000.0, "execution_time": 3600})

    def test_get_execution_attribution_missing(self):
        asset_id = str(uuid4())
        attribution_data = {
            "other_asset": {"inference_cost": 1000.0, "execution_time": 3600}
        }
        self.adapter.consume_icae_attribution(attribution_data)

        result = self.adapter.get_execution_attribution(UUID(asset_id))
        self.assertIsNone(result)
        
    def test_pydantic_validation(self):
        # Test that Pydantic validation works
        attribution_data = {
            "asset_1": {
                "asset_id": "asset_1",
                "inference_cost": 1000.0,
                "execution_time": 3600.0,
                "timestamp": datetime.now(),
                "model_version": "v1.0"
            }
        }
        
        self.adapter.consume_icae_attribution(attribution_data)
        
        # Should have validated data
        self.assertIn("asset_1", self.adapter.icae_data)
        self.assertIsInstance(self.adapter.icae_data["asset_1"], ICAEAttribution)
        
    def test_pydantic_validation_error(self):
        # Test that invalid data raises error
        attribution_data = {
            "asset_1": {
                "asset_id": "asset_1",
                "inference_cost": -1000.0,  # Invalid negative cost
                "execution_time": 3600.0,
                "timestamp": datetime.now(),
                "model_version": "v1.0"
            }
        }
        
        with self.assertRaises(ValueError):
            self.adapter.consume_icae_attribution(attribution_data)


if __name__ == '__main__':
    unittest.main()