import unittest
from uuid import UUID, uuid4

from icl.core import (
    IntelligenceCapitalLedger,
    CapitalProofGenerator,
    IntelligenceAsset,
    DepreciationMethod
)


class TestCapitalProofs(unittest.TestCase):
    def setUp(self):
        self.ledger = IntelligenceCapitalLedger()
        self.proof_generator = CapitalProofGenerator(self.ledger)

    def test_generate_asset_proof(self):
        asset_id = uuid4()
        self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        proof = self.proof_generator.generate_asset_proof(asset_id)

        self.assertIsNotNone(proof)
        self.assertEqual(proof.asset_id, asset_id)
        self.assertEqual(proof.origin, "ICL")
        self.assertIsNotNone(proof.proof_hash)
        # Should have previous hash if there are other proofs
        self.assertIsNone(proof.previous_proof_hash)  # First proof has no previous

    def test_generate_execution_proof(self):
        asset_id = uuid4()
        self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        proof = self.proof_generator.generate_execution_proof(asset_id)

        self.assertIsNotNone(proof)
        self.assertEqual(proof.asset_id, asset_id)

    def test_reconstruct_proof(self):
        asset_id = uuid4()
        self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        proof = self.proof_generator.generate_asset_proof(asset_id)
        reconstructed = self.proof_generator.reconstruct_proof(proof.proof_id)

        self.assertIsNotNone(reconstructed)
        self.assertEqual(reconstructed.proof_id, proof.proof_id)

    def test_get_asset_history(self):
        asset_id = uuid4()
        self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        history = self.proof_generator.get_asset_history(asset_id)
        self.assertEqual(len(history), 0)  # No events yet

        # Add an event
        from icl.core import CapitalEvent
        from datetime import datetime

        event = CapitalEvent(
            event_id=uuid4(),
            asset_id=asset_id,
            event_type="utilization",
            timestamp=datetime.now(),
            details={"amount": 500.0}
        )
        self.ledger.record_event(event)

        history = self.proof_generator.get_asset_history(asset_id)
        self.assertEqual(len(history), 1)
        
    def test_proof_hash_chain(self):
        # Test that proofs form a proper chain
        asset_id = uuid4()
        self.ledger.create_asset(
            asset_id=asset_id,
            owner="team-alpha",
            initial_value=10000.0,
            depreciation_method=DepreciationMethod.LINEAR,
            useful_life_months=12
        )

        # Generate first proof
        proof1 = self.proof_generator.generate_asset_proof(asset_id)
        
        # Generate second proof
        proof2 = self.proof_generator.generate_asset_proof(asset_id)
        
        # Second should reference first
        self.assertEqual(proof2.previous_proof_hash, proof1.proof_hash)


if __name__ == '__main__':
    unittest.main()