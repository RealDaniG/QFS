#!/usr/bin/env python
"""
explain_hsmf_action.py - CLI Tool for Human-Readable HSMF Explanations

Reconstructs and explains HSMF calculations in plain language.
Useful for debugging, auditing, and understanding action costs/rewards.

Usage:
    python explain_hsmf_action.py --s_res 100 --s_flx 50 --s_psi_sync 75 --f_atr 25 --s_chr 800
    python explain_hsmf_action.py --json '{"s_res": 100, "s_flx": 50, ...}'
    python explain_hsmf_action.py --proof-log /path/to/hsmf_proof.json

References:
    - docs/HSMF_MathContracts.md
    - core/HSMF.py (HSMFProof dataclass)
"""

import argparse
import json
import sys
import os
from typing import Dict, Any

# Add parent directory (v13) and its parent (V13) to path for imports
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_V13_DIR = os.path.dirname(_THIS_DIR)
_REPO_DIR = os.path.dirname(_V13_DIR)

for p in [_REPO_DIR, _V13_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.core.HSMF import HSMF, HSMFProof
except ImportError:
    # Fallback for direct execution from v13 directory
    from libs.BigNum128 import BigNum128
    from libs.CertifiedMath import CertifiedMath
    from core.HSMF import HSMF, HSMFProof


def compute_hsmf_metrics(
    s_res: int,
    s_flx: int,
    s_psi_sync: int,
    f_atr: int,
    s_chr: int,
    lambda1: int = 1,
    lambda2: int = 1,
) -> Dict[str, Any]:
    """
    Compute HSMF metrics from integer inputs.

    Returns a dict with all computed values and their decimal representations.
    """
    cm = CertifiedMath()
    hsmf = HSMF(cm)
    log_list = []

    # Convert to BigNum128
    bn_s_res = BigNum128.from_int(s_res)
    bn_s_flx = BigNum128.from_int(s_flx)
    bn_s_psi_sync = BigNum128.from_int(s_psi_sync)
    bn_f_atr = BigNum128.from_int(f_atr)
    bn_s_chr = BigNum128.from_int(s_chr)
    bn_lambda1 = BigNum128.from_int(lambda1)
    bn_lambda2 = BigNum128.from_int(lambda2)

    # Compute action cost
    action_cost = hsmf._calculate_action_cost_qfs(
        bn_s_res,
        bn_s_flx,
        bn_s_psi_sync,
        bn_f_atr,
        bn_lambda1,
        bn_lambda2,
        log_list,
        None,
    )

    # Compute c_holo
    c_holo = hsmf._calculate_c_holo(bn_s_res, bn_s_flx, bn_s_psi_sync, log_list, None)

    # Compute rewards
    metrics = {
        "s_chr": bn_s_chr,
        "c_holo": c_holo,
        "s_res": bn_s_res,
        "s_flx": bn_s_flx,
        "s_psi_sync": bn_s_psi_sync,
        "f_atr": bn_f_atr,
        "action_cost": action_cost,
    }
    rewards = hsmf._compute_hsmf_rewards(metrics, log_list)

    return {
        "inputs": {
            "s_res": s_res,
            "s_flx": s_flx,
            "s_psi_sync": s_psi_sync,
            "f_atr": f_atr,
            "s_chr": s_chr,
            "lambda1": lambda1,
            "lambda2": lambda2,
        },
        "outputs": {
            "action_cost": action_cost.to_decimal_string(),
            "c_holo": c_holo.to_decimal_string(),
            "chr_reward": rewards["chr_reward"].to_decimal_string(),
            "flx_reward": rewards["flx_reward"].to_decimal_string(),
            "res_reward": rewards["res_reward"].to_decimal_string(),
            "psi_sync_reward": rewards["psi_sync_reward"].to_decimal_string(),
            "atr_reward": rewards["atr_reward"].to_decimal_string(),
            "total_reward": rewards["total_reward"].to_decimal_string(),
        },
        "raw_values": {
            "action_cost": action_cost.value,
            "c_holo": c_holo.value,
            "total_reward": rewards["total_reward"].value,
        },
    }


def format_explanation(result: Dict[str, Any]) -> str:
    """Format HSMF computation results as human-readable text."""
    inputs = result["inputs"]
    outputs = result["outputs"]

    lines = [
        "=" * 60,
        "HSMF Action Explanation",
        "=" * 60,
        "",
        "INPUTS",
        "-" * 40,
        f"  S_RES (Resistance):       {inputs['s_res']:>12}",
        f"  S_FLX (Flux Deviation):   {inputs['s_flx']:>12}",
        f"  S_PSI_SYNC (Psi Sync):    {inputs['s_psi_sync']:>12}",
        f"  F_ATR (ATR Factor):       {inputs['f_atr']:>12}",
        f"  S_CHR (Coherence):        {inputs['s_chr']:>12}",
        f"  Lambda1 (Flux Weight):    {inputs['lambda1']:>12}",
        f"  Lambda2 (Psi Weight):     {inputs['lambda2']:>12}",
        "",
        "COMPUTED METRICS",
        "-" * 40,
    ]

    # Parse action cost formula
    total_dissonance = inputs["s_res"] + inputs["s_flx"] + inputs["s_psi_sync"]
    lines.extend(
        [
            f"  Total Dissonance = S_RES + S_FLX + S_PSI_SYNC",
            f"                   = {inputs['s_res']} + {inputs['s_flx']} + {inputs['s_psi_sync']}",
            f"                   = {total_dissonance}",
            "",
            f"  C_holo = 1 / (1 + Total_Dissonance)",
            f"         = 1 / (1 + {total_dissonance})",
            f"         = {outputs['c_holo']}",
            "",
            f"  Action Cost = S_RES + (λ₁ × S_FLX) + (λ₂ × S_PSI_SYNC) + F_ATR",
            f"              = {inputs['s_res']} + ({inputs['lambda1']} × {inputs['s_flx']}) + ({inputs['lambda2']} × {inputs['s_psi_sync']}) + {inputs['f_atr']}",
            f"              = {outputs['action_cost']}",
        ]
    )

    lines.extend(
        [
            "",
            "REWARD BREAKDOWN",
            "-" * 40,
            f"  CHR Reward:       {outputs['chr_reward']:>25}",
            f"  FLX Reward:       {outputs['flx_reward']:>25}",
            f"  RES Reward:       {outputs['res_reward']:>25}",
            f"  PSI_SYNC Reward:  {outputs['psi_sync_reward']:>25}",
            f"  ATR Reward:       {outputs['atr_reward']:>25}",
            "-" * 40,
            f"  TOTAL REWARD:     {outputs['total_reward']:>25}",
            "",
            "=" * 60,
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Explain HSMF action cost and reward calculations"
    )

    # Input options
    parser.add_argument("--s_res", type=int, help="Resistance metric (default: 0)")
    parser.add_argument("--s_flx", type=int, help="Flux deviation (default: 0)")
    parser.add_argument(
        "--s_psi_sync", type=int, help="Psi sync deviation (default: 0)"
    )
    parser.add_argument("--f_atr", type=int, help="ATR factor (default: 0)")
    parser.add_argument("--s_chr", type=int, help="Coherence metric (default: 1000)")
    parser.add_argument(
        "--lambda1", type=int, default=1, help="Flux weight (default: 1)"
    )
    parser.add_argument(
        "--lambda2", type=int, default=1, help="Psi weight (default: 1)"
    )

    # JSON input
    parser.add_argument("--json", type=str, help="JSON string with all inputs")

    # Output options
    parser.add_argument("--output-json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Parse inputs
    if args.json:
        data = json.loads(args.json)
        s_res = data.get("s_res", 0)
        s_flx = data.get("s_flx", 0)
        s_psi_sync = data.get("s_psi_sync", 0)
        f_atr = data.get("f_atr", 0)
        s_chr = data.get("s_chr", 1000)
        lambda1 = data.get("lambda1", 1)
        lambda2 = data.get("lambda2", 1)
    else:
        s_res = args.s_res if args.s_res is not None else 0
        s_flx = args.s_flx if args.s_flx is not None else 0
        s_psi_sync = args.s_psi_sync if args.s_psi_sync is not None else 0
        f_atr = args.f_atr if args.f_atr is not None else 0
        s_chr = args.s_chr if args.s_chr is not None else 1000
        lambda1 = args.lambda1
        lambda2 = args.lambda2

    # Compute
    result = compute_hsmf_metrics(
        s_res=s_res,
        s_flx=s_flx,
        s_psi_sync=s_psi_sync,
        f_atr=f_atr,
        s_chr=s_chr,
        lambda1=lambda1,
        lambda2=lambda2,
    )

    # Output
    if args.output_json:
        print(json.dumps(result, indent=2))
    else:
        print(format_explanation(result))


if __name__ == "__main__":
    main()
