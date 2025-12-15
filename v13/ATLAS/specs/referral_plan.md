
# C-005 Referral System Plan

## Backend

1. **Users API (`api/users.py`)**:
    * Add `GET /v1/users/{wallet}/referrals`
    * Logic: Replay `GenesisLedger` for `REFERRAL_USE` events where `referral_code` matches user's code.
    * Return: `{ count: int, recent_referees: [] }`.

## Frontend

1. **WalletConnect (`WalletConnect.tsx`)**:
    * On Mount: Check URL for `?ref=CODE`.
    * Store in `localStorage` ("pending_referral").
    * On Login: Pass `referral_code` from storage to `connect-wallet` API.
    * On Success: Clear storage.

2. **Profile Page (`profile.tsx`)**:
    * Add "Referral Dashboard" section.
    * Display `referral_code` (from existing profile).
    * Display Stats (from new endpoint).
    * Copy Link button.

## Zero-Sim

* Stats derived strictly from Ledger events. No external DB.
