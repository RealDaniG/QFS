"""
economic_constants.py - Constitutional Economic Parameters for QFS V13.5

Contains fixed-point constants for economic parameters to ensure structural determinism,
governance safety, and audit completeness. This file serves as the economic constitution
of the QFS V13.5 system.

IMPORTANT: Constants marked with [IMMUTABLE] cannot be changed via governance.
           Constants marked with [MUTABLE] can be changed via hard fork only.
           All changes require epoch-bound protocol upgrade via PBFT consensus.
"""

try:
    from ..CertifiedMath import BigNum128
except ImportError:
    try:
        from src.libs.CertifiedMath import BigNum128
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from CertifiedMath import BigNum128


# =============================================================================
# SECTION 1: GLOBAL MATH & EPOCH RULES [IMMUTABLE]
# =============================================================================

# Deterministic Math Rules
FIXED_POINT_SCALE = BigNum128.from_int(10**18)  # [IMMUTABLE] 1e18 SCALE
ROUNDING_MODE = "FLOOR"  # [IMMUTABLE] must never be BANKERS or stochastic

# Epoch & Block Timing
BLOCKS_PER_EPOCH = BigNum128.from_int(512)  # [MUTABLE] ~2.4 hours at 17s/block
BLOCK_TIME_SECONDS = BigNum128.from_int(17)  # [MUTABLE] average block time
UPGRADE_ACTIVATION_DELAY_EPOCHS = BigNum128.from_int(2)  # [IMMUTABLE] safety delay

# System-Wide Bounds
MAX_TOTAL_SUPPLY_RATIO_CHANGE = BigNum128.from_string("0.02")  # [IMMUTABLE] 2% per epoch max
MAX_SINGLE_EVENT_IMPACT = BigNum128.from_string("0.05")  # [IMMUTABLE] 5% max impact
SYSTEM_DECAY_EPOCHS = BigNum128.from_int(10)  # [MUTABLE] decay period

# System Parameters (from original)
SYSTEM_BETA_PENALTY = BigNum128.from_int(100000000)  # [MUTABLE] β_penalty = 100,000,000
GOLDEN_RATIO = BigNum128(1618033988749894848)  # [IMMUTABLE] φ (golden ratio) * 1e18


# =============================================================================
# SECTION 2: CHR (COHERENCE / VALUE CREATION) CONSTANTS
# =============================================================================

# Issuance Bounds
CHR_BASE_REWARD = BigNum128.from_int(1000)  # [MUTABLE] base reward per coherent action
CHR_MAX_REWARD_PER_ACTION = BigNum128.from_int(10000)  # [IMMUTABLE] hard cap
CHR_MIN_REWARD_PER_ACTION = BigNum128.from_int(10)  # [IMMUTABLE] hard floor

# Emission Controls
CHR_DAILY_EMISSION_CAP = BigNum128.from_int(10_000_000)  # [MUTABLE] total daily cap
CHR_DECAY_RATE = BigNum128.from_string("0.995")  # [MUTABLE] epoch-based decay
CHR_SATURATION_THRESHOLD = BigNum128.from_int(1_000_000_000)  # [MUTABLE] max supply


# =============================================================================
# SECTION 3: FLX (REPUTATION / VISIBILITY) CONSTANTS
# =============================================================================

# Reward Fraction
FLX_REWARD_FRACTION = BigNum128.from_string("0.10")  # [MUTABLE] 10% of CHR reward
MAX_FLX_REWARD_FRACTION = BigNum128.from_string("0.20")  # [IMMUTABLE] hard cap 20%
MIN_FLX_REWARD_FRACTION = BigNum128.from_string("0.01")  # [IMMUTABLE] hard floor 1%

# Per-User Bounds
FLX_MAX_PER_USER = BigNum128.from_int(1_000_000)  # [MUTABLE] prevents single-user dominance
FLX_DECAY_RATE = BigNum128.from_string("0.99")  # [MUTABLE] inactivity decay per epoch
FLX_MIN_EFFECTIVE_BALANCE = BigNum128.from_int(100)  # [MUTABLE] minimum effective balance

# Visibility & Governance
FLX_VISIBILITY_WEIGHT_CAP = BigNum128.from_string("5.0")  # [MUTABLE] max visibility multiplier
FLX_GOVERNANCE_WEIGHT_MULTIPLIER = BigNum128.from_string("1.0")  # [MUTABLE] governance weight


# =============================================================================
# SECTION 4: PSI (TEMPORAL / PREDICTIVE STABILITY) CONSTANTS
# =============================================================================

# Memory & Prediction
PSI_MEMORY_WINDOW_BLOCKS = BigNum128.from_int(2048)  # [MUTABLE] ~9.7 hours lookback

# Volatility Clamps
PSI_MAX_DELTA_PER_EPOCH = BigNum128.from_string("0.10")  # [IMMUTABLE] 10% max change
PSI_MIN_DELTA_MAGNITUDE = BigNum128.from_string("0.10")  # [IMMUTABLE] 10% max decrease magnitude

# Saturation & Decay
PSI_SATURATION_CAP = BigNum128.from_int(1_000_000)  # [MUTABLE] max PSI accumulation
PSI_DECAY_RATE = BigNum128.from_string("0.997")  # [MUTABLE] trend decay


# =============================================================================
# SECTION 5: ATR (ACTION / ANTI-ABUSE) CONSTANTS
# =============================================================================

# Base Costs
ATR_BASE_ACTION_COST = BigNum128.from_int(1000)  # [MUTABLE] base action cost
ATR_BASE_COST = BigNum128.from_int(1000)  # [MUTABLE] alias for compatibility

# Abuse Detection
ATR_ABUSE_THRESHOLD = BigNum128.from_string("2.0")  # [MUTABLE] multiplier threshold
ATR_MAX_COST_MULTIPLIER = BigNum128.from_string("10.0")  # [IMMUTABLE] hard cap on penalties
ATR_MAX_ACCUMULATION = BigNum128.from_int(100_000)  # [MUTABLE] max accumulated penalty

# Recovery & Forgiveness
ATR_DECAY_RATE = BigNum128.from_string("0.98")  # [MUTABLE] per epoch decay
ATR_RECOVERY_RATE = BigNum128.from_string("0.95")  # [MUTABLE] forgiveness rate per epoch
ATR_COOLDOWN_BLOCKS = BigNum128.from_int(120)  # [MUTABLE] ~34 min cooldown

# Escalation
ATR_ESCALATION_MULTIPLIER = BigNum128.from_string("1.5")  # [MUTABLE] repeat offense multiplier


# =============================================================================
# SECTION 6: RES (RESERVE / STABILITY BUFFER) CONSTANTS
# =============================================================================

# Target Reserve Ratios
RES_TARGET_RATIO = BigNum128.from_string("0.20")  # [MUTABLE] 20% of total issuance
RES_EMERGENCY_FLOOR = BigNum128.from_int(1_000_000)  # [IMMUTABLE] minimum reserve

# Drawdown & Replenishment
RES_MAX_DRAW_PER_EPOCH = BigNum128.from_string("0.05")  # [IMMUTABLE] 5% max draw
RES_REPLENISH_RATE = BigNum128.from_string("0.10")  # [MUTABLE] 10% replenishment rate


# =============================================================================
# SECTION 7: NOD (NODE OPERATOR DETERMINATION) CONSTANTS
# =============================================================================

# Allocation Fraction
NOD_ALLOCATION_FRACTION = BigNum128.from_string("0.10")  # [MUTABLE] 10% of ATR fees
MAX_NOD_ALLOCATION_FRACTION = BigNum128.from_string("0.15")  # [IMMUTABLE] hard cap 15%
MIN_NOD_ALLOCATION_FRACTION = BigNum128.from_string("0.01")  # [IMMUTABLE] hard floor 1%

# Governance
NOD_DEFAULT_QUORUM_THRESHOLD = BigNum128.from_string("0.66")  # [MUTABLE] 66% quorum
MAX_QUORUM_THRESHOLD = BigNum128.from_string("0.90")  # [IMMUTABLE] 90% max
MIN_QUORUM_THRESHOLD = BigNum128.from_string("0.51")  # [IMMUTABLE] 51% min

# Emission Controls
NOD_MIN_ACTIVE_NODES = BigNum128.from_int(3)  # [IMMUTABLE] minimum network size
NOD_MAX_ISSUANCE_PER_EPOCH = BigNum128.from_string("1000000")  # [MUTABLE] max epoch issuance
NOD_ZERO_ACTIVITY_FLOOR = BigNum128.from_int(0)  # [IMMUTABLE] no issuance when idle

# Anti-Centralization
MAX_NOD_VOTING_POWER_RATIO = BigNum128.from_string("0.25")  # [IMMUTABLE] 25% per node cap
MAX_NODE_REWARD_SHARE = BigNum128.from_string("0.30")  # [IMMUTABLE] 30% max reward share


# =============================================================================
# SECTION 8: REWARD DISTRIBUTION BOUNDS [V13.6]
# =============================================================================

# Per-Address Reward Caps (for RewardAllocator)
MAX_REWARD_PER_ADDRESS = BigNum128.from_int(1_000_000)  # [MUTABLE] prevents single-address capture
MIN_DUST_THRESHOLD = BigNum128.from_int(1)  # [IMMUTABLE] minimum meaningful reward


# =============================================================================
# SECTION 9: GOVERNANCE TIMING & COOLDOWNS [IMMUTABLE]
# =============================================================================

# Proposal Lifecycle
GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS = BigNum128.from_int(120)  # [IMMUTABLE] ~34 min between proposals
GOVERNANCE_VOTING_WINDOW_BLOCKS = BigNum128.from_int(720)  # [MUTABLE] ~3.4 hours voting
GOVERNANCE_EXECUTION_DELAY_BLOCKS = BigNum128.from_int(240)  # [IMMUTABLE] ~1.1 hours delay

# Upgrade Safety
GOVERNANCE_EMERGENCY_QUORUM = BigNum128.from_string("0.80")  # [IMMUTABLE] 80% for emergency
GOVERNANCE_PARAMETER_CHANGE_COOLDOWN_EPOCHS = BigNum128.from_int(2)  # [IMMUTABLE] 2 epoch cooldown
