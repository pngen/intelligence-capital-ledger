from typing import Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ValidationError
from datetime import datetime


class ICAEAttribution(BaseModel):
    """Schema for ICAE attribution data."""
    asset_id: str = Field(..., description="UUID of the intelligence asset")
    inference_cost: float = Field(..., gt=0, description="Cost in dollars")
    execution_time: float = Field(..., gt=0, description="Time in seconds")
    timestamp: datetime
    model_version: str


class IntegrationAdapter:
    """Handles integration with external systems."""

    def __init__(self):
        self.icae_data = {}  # Simulated ICAE data source
        self.financial_systems = []  # Simulated financial systems

    def consume_icae_attribution(self, attribution_data: Dict[str, Any]) -> None:
        """Consume inference attribution from ICAE."""
        validated_data = {}
        for key, value in attribution_data.items():
            if isinstance(value, dict):
                try:
                    validated_data[key] = ICAEAttribution(**value)
                except ValidationError as e:
                    raise ValueError(f"Invalid attribution data for {key}: {e}")
            else:
                validated_data[key] = value
        
        self.icae_data.update(validated_data)

    def emit_to_financial_system(self, event) -> bool:
        """Emit capital events to financial systems."""
        # In a real implementation, this would integrate with actual financial systems
        return True

    def validate_attribution(self, asset_id: UUID, execution_details: Dict[str, Any]) -> bool:
        """Validate that attribution exists for an execution."""
        # Check if we have sufficient attribution data
        if not self.icae_data.get(str(asset_id)):
            return False
        return True

    def get_execution_attribution(self, asset_id: UUID) -> Optional[Dict[str, Any]]:
        """Get attribution data for a specific execution."""
        return self.icae_data.get(str(asset_id))

    def reconcile_with_financial_systems(self) -> Dict[str, Any]:
        """Reconcile ICL data with financial systems."""
        # In a real implementation, this would perform actual reconciliation
        return {
            "status": "reconciled",
            "timestamp": "2023-01-01T00:00:00Z"
        }