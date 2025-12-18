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
        from v13.libs.CertifiedMath import BigNum128
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from CertifiedMath import BigNum128
FIXED_POINT_SCALE = BigNum128.from_int(10 ** 18)
ROUNDING_MODE = 'FLOOR'
BLOCKS_PER_EPOCH = BigNum128.from_int(512)
BLOCK_TIME_SECONDS = BigNum128.from_int(17)
UPGRADE_ACTIVATION_DELAY_EPOCHS = BigNum128.from_int(2)
MAX_TOTAL_SUPPLY_RATIO_CHANGE = BigNum128.from_string('0.02')
MAX_SINGLE_EVENT_IMPACT = BigNum128.from_string('0.05')
SYSTEM_DECAY_EPOCHS = BigNum128.from_int(10)
SYSTEM_BETA_PENALTY = BigNum128.from_int(100000000)
GOLDEN_RATIO = BigNum128(1618033988749894848)
CHR_BASE_REWARD = BigNum128.from_int(1000)
CHR_MAX_REWARD_PER_ACTION = BigNum128.from_int(10000)
CHR_MIN_REWARD_PER_ACTION = BigNum128.from_int(10)
CHR_DAILY_EMISSION_CAP = BigNum128.from_int(10000000)
CHR_DECAY_RATE = BigNum128.from_string('0.995')
CHR_SATURATION_THRESHOLD = BigNum128.from_int(1000000000)
FLX_REWARD_FRACTION = BigNum128.from_string('0.10')
MAX_FLX_REWARD_FRACTION = BigNum128.from_string('0.20')
MIN_FLX_REWARD_FRACTION = BigNum128.from_string('0.01')
FLX_MAX_PER_USER = BigNum128.from_int(1000000)
FLX_DECAY_RATE = BigNum128.from_string('0.99')
FLX_MIN_EFFECTIVE_BALANCE = BigNum128.from_int(100)
FLX_VISIBILITY_WEIGHT_CAP = BigNum128.from_string('5.0')
FLX_GOVERNANCE_WEIGHT_MULTIPLIER = BigNum128.from_string('1.0')
PSI_MEMORY_WINDOW_BLOCKS = BigNum128.from_int(2048)
PSI_MAX_DELTA_PER_EPOCH = BigNum128.from_string('0.10')
PSI_MIN_DELTA_MAGNITUDE = BigNum128.from_string('0.10')
PSI_SATURATION_CAP = BigNum128.from_int(1000000)
PSI_DECAY_RATE = BigNum128.from_string('0.997')
ATR_BASE_ACTION_COST = BigNum128.from_int(1000)
ATR_BASE_COST = BigNum128.from_int(1000)
ATR_ABUSE_THRESHOLD = BigNum128.from_string('2.0')
ATR_MAX_COST_MULTIPLIER = BigNum128.from_string('10.0')
ATR_MAX_ACCUMULATION = BigNum128.from_int(100000)
ATR_DECAY_RATE = BigNum128.from_string('0.98')
ATR_RECOVERY_RATE = BigNum128.from_string('0.95')
ATR_COOLDOWN_BLOCKS = BigNum128.from_int(120)
ATR_ESCALATION_MULTIPLIER = BigNum128.from_string('1.5')
RES_TARGET_RATIO = BigNum128.from_string('0.20')
RES_EMERGENCY_FLOOR = BigNum128.from_int(1000000)
RES_MAX_DRAW_PER_EPOCH = BigNum128.from_string('0.05')
RES_REPLENISH_RATE = BigNum128.from_string('0.10')
NOD_ALLOCATION_FRACTION = BigNum128.from_string('0.10')
MAX_NOD_ALLOCATION_FRACTION = BigNum128.from_string('0.15')
MIN_NOD_ALLOCATION_FRACTION = BigNum128.from_string('0.01')
NOD_DEFAULT_QUORUM_THRESHOLD = BigNum128.from_string('0.66')
MAX_QUORUM_THRESHOLD = BigNum128.from_string('0.90')
MIN_QUORUM_THRESHOLD = BigNum128.from_string('0.51')
NOD_MIN_ACTIVE_NODES = BigNum128.from_int(3)
NOD_MAX_ISSUANCE_PER_EPOCH = BigNum128.from_string('1000000')
NOD_ZERO_ACTIVITY_FLOOR = BigNum128.from_int(0)
MAX_NOD_VOTING_POWER_RATIO = BigNum128.from_string('0.25')
MAX_NODE_REWARD_SHARE = BigNum128.from_string('0.30')
MAX_REWARD_PER_ADDRESS = BigNum128.from_int(1000000)
MIN_DUST_THRESHOLD = BigNum128.from_int(1)
GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS = BigNum128.from_int(120)
GOVERNANCE_VOTING_WINDOW_BLOCKS = BigNum128.from_int(720)
GOVERNANCE_EXECUTION_DELAY_BLOCKS = BigNum128.from_int(240)
GOVERNANCE_EMERGENCY_QUORUM = BigNum128.from_string('0.80')
GOVERNANCE_PARAMETER_CHANGE_COOLDOWN_EPOCHS = BigNum128.from_int(2)
