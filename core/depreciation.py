from datetime import datetime, timedelta
from typing import Tuple

from .types import IntelligenceAsset, DepreciationMethod


def calculate_depreciation(
    asset: IntelligenceAsset,
    start_date: datetime,
    end_date: datetime,
    salvage_value: float = 0.0,
    rate_multiplier: float = 2.0
) -> Tuple[float, float]:
    """
    Calculate depreciation for an intelligence asset over a period.
    
    Args:
        asset: The intelligence asset to depreciate
        start_date: Start of the depreciation period
        end_date: End of the depreciation period
        salvage_value: Value remaining after full depreciation (default 0.0)
        rate_multiplier: For declining balance method (default 2.0 for double-declining)
    
    Returns:
        Tuple of (depreciated_amount, new_value)
    """
    if asset.depreciation_method == DepreciationMethod.LINEAR:
        return _linear_depreciation(asset, start_date, end_date, salvage_value)
    elif asset.depreciation_method == DepreciationMethod.DECLINING_BALANCE:
        return _declining_balance_depreciation(asset, start_date, end_date, salvage_value, rate_multiplier)
    else:
        raise ValueError(f"Unsupported depreciation method: {asset.depreciation_method}")


def _linear_depreciation(
    asset: IntelligenceAsset,
    start_date: datetime,
    end_date: datetime,
    salvage_value: float = 0.0
) -> Tuple[float, float]:
    """
    Calculate linear (straight-line) depreciation.
    
    Formula: D = (C - S) / N
    Where:
        D = Depreciation per period
        C = Cost (initial_value)
        S = Salvage value
        N = Useful life in periods
    
    For partial periods: D_partial = D * (months / total_months)
    """
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    
    if months <= 0:
        return 0.0, asset.current_value or asset.initial_value
    
    # Calculate monthly depreciation amount
    depreciable_base = asset.initial_value - salvage_value
    monthly_rate = 1.0 / asset.useful_life_months
    depreciation_amount = depreciable_base * monthly_rate * months
    
    new_value = max(salvage_value, asset.current_value or asset.initial_value - depreciation_amount)
    
    return depreciation_amount, new_value


def _declining_balance_depreciation(
    asset: IntelligenceAsset,
    start_date: datetime,
    end_date: datetime,
    salvage_value: float = 0.0,
    rate_multiplier: float = 2.0
) -> Tuple[float, float]:
    """
    Calculate declining balance depreciation.
    
    Formula: D = Current Value * Rate
    Where:
        Rate = (Rate Multiplier / Useful Life)
        Switches to straight-line when remaining value is less than straight-line amount
    
    For partial periods: Apply rate for each month in period
    """
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    
    if months <= 0:
        return 0.0, asset.current_value or asset.initial_value
    
    # Calculate rate based on useful life and multiplier
    rate = rate_multiplier / asset.useful_life_months
    current_value = asset.current_value or asset.initial_value
    
    # Apply depreciation for each month
    depreciation_amount = 0.0
    for _ in range(months):
        monthly_depreciation = current_value * rate
        if current_value - monthly_depreciation < salvage_value:
            # Switch to straight-line for final period
            depreciation_amount += (current_value - salvage_value)
            break
        else:
            depreciation_amount += monthly_depreciation
            current_value -= monthly_depreciation
    
    new_value = max(salvage_value, asset.current_value or asset.initial_value - depreciation_amount)
    
    return depreciation_amount, new_value