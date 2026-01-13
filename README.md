# Intelligence Capital Ledger (ICL)

## One-sentence value proposition

A deterministic, audit-grade accounting system for intelligence capital that converts inference execution into CFO-ready financial artifacts.

## Overview

The Intelligence Capital Ledger (ICL) is a financial governance system designed to treat intelligence as institutional capital rather than an operational expense. It provides a structured approach to capitalizing, allocating, depreciating, and realizing returns from intelligence assets while maintaining full auditability and compliance with accounting standards.

ICL operates above inference attribution systems (like ICAE) and below financial governance layers, formalizing the economic meaning of intelligence execution without re-computing attribution or replacing existing ERP systems.

## Architecture diagram
<pre>
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Inference      │    │  Intelligence    │    │  Financial       │
│  Attribution    │───▶│  Capital Ledger  │───▶│  Reporting       │
│  (ICAE)         │    │  (ICL)           │    │  Systems         │
└─────────────────┘    └──────────────────┘    └──────────────────┘
         │
         ▼
┌─────────────────┐
│  Audit &        │
│  Compliance     │
│  Tooling        │
└─────────────────┘
</pre>

## Core Components

1. **IntelligenceAsset**: A capitalized unit of intelligence capability with owner, value, and depreciation rules.
2. **CapitalEvent**: Discrete economic actions affecting intelligence capital (allocation, utilization, depreciation).
3. **LedgerEntry**: Immutable, time-ordered financial records derived from capital events.
4. **JournalEntry**: Double-entry accounting journal entries for proper financial statement generation.
5. **CapitalProof**: Machine-verifiable explanations of financial figures for audit purposes.
6. **DepreciationEngine**: Calculates asset value decay using configurable methods.
7. **LifecycleManager**: Orchestrates the complete asset lifecycle from capitalization to retirement.
8. **IntegrityChecker**: Ensures data consistency and prevents invalid operations.
9. **IntegrationAdapter**: Bridges with external systems like ICAE and financial platforms.

## Usage

```python
from icl.core import (
    IntelligenceCapitalLedger,
    IntelligenceCapitalLifecycle,
    DepreciationMethod
)
from uuid import uuid4

# Initialize ledger and lifecycle manager
ledger = IntelligenceCapitalLedger()
lifecycle = IntelligenceCapitalLifecycle(ledger)

# Capitalize an intelligence asset
asset_id = uuid4()
asset = lifecycle.capitalize(
    asset_id=asset_id,
    owner="Ledger Owner",
    initial_value=100000.0,
    depreciation_method=DepreciationMethod.LINEAR,
    useful_life_months=24
)

# Allocate the asset to a new owner
lifecycle.allocate(asset_id, "Product Engineering")

# Record utilization
lifecycle.utilize(asset_id, 5000.0)

# Apply depreciation
from datetime import datetime
start = datetime(2023, 1, 1)
end = datetime(2023, 6, 1)
lifecycle.depreciate(asset_id, start, end)

# Generate audit proof
proof = ledger.generate_proof(asset_id)
```

## Design Principles
- **Deterministic**: All financial outcomes are predictable and reproducible.
- **Audit-ready**: Every transaction is traceable with machine-verifiable proofs.
- **Accounting-legible**: All primitives map directly to accounting concepts.
- **Immutable**: Once recorded, data cannot be altered or retroactively modified.
- **Composable**: Components can be integrated independently without tight coupling.
- **Resilient**: Failure modes are explicit and do not compromise system integrity.

## Requirements
1. **Capital Lifecycle Management**
- Asset capitalization with owner, value, and depreciation rules
- Allocation between business units
- Utilization tracking
- Depreciation calculation using configurable methods
- Retirement and write-off procedures

2. **Ledger Semantics**
- Append-only, immutable ledger entries
- Time-ordered transactions
- Deterministic financial outcomes
- No silent revaluation or aggregation without traceability

3. **Integrity Model**
- Prevents retroactive modifications
- Detects and fails on invalid data
- Maintains audit trail integrity
- Ensures no unowned intelligence execution

4. **Auditability**
- Capital proofs for all financial figures
- Complete asset history tracking
- Reconstructable audit trails
- Integration-ready with compliance tooling

5. **Integration Model**
- Consumes inference attribution from ICAE
- Emits to financial reporting systems
- Supports cross-system reconciliation
- Operates without assuming control over execution or finance platforms

6. **Versioning Contract (v1.0.0)**
- Stable API for core data structures
- Immutable ledger semantics
- Deterministic depreciation calculations
- Audit-ready proof generation