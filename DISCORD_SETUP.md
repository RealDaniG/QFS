# Discord Integration Setup

## Overview

Discord notifications provide operational visibility for QFS v15 pipeline status without creating alert fatigue.

## Setup Instructions

### 1. Create Discord Webhook

1. Go to your Discord server
2. Navigate to Server Settings → Integrations → Webhooks
3. Click "New Webhook"
4. Name it "QFS CI Pipeline"
5. Select channel: `#qfs-ci` (private, for team)
6. Copy the webhook URL

### 2. Add GitHub Secret

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `DISCORD_WEBHOOK_URL`
4. Value: Paste the webhook URL from step 1
5. Click "Add secret"

### 3. Test Notification

```bash
# Set webhook URL
export DISCORD_WEBHOOK_URL="your-webhook-url-here"

# Test success notification
python notify_discord.py \
  --type success \
  --commit a3f5b2c1 \
  --branch main \
  --tag v15.0.0

# Test failure notification
python notify_discord.py \
  --type failure \
  --commit a3f5b2c1 \
  --branch main \
  --failed-stages A B

# Test deployment notification
python notify_discord.py \
  --type deployment \
  --commit a3f5b2c1 \
  --tag v15.0.0 \
  --deployment-success
```

## What Gets Notified

### Pipeline Success (Green)

**Triggers:** Push to `main`, `release/*`, or tags  
**Message:**

- ✅ Pipeline SUCCESS
- Commit SHA and branch/tag
- All stages A–E status
- "HEAD is deployable to testnet"

### Pipeline Failure (Red)

**Triggers:** Any stage fails on `main`, `release/*`, or tags  
**Message:**

- ❌ Pipeline FAILURE
- Commit SHA and branch/tag
- List of failed stages
- "DO NOT DEPLOY - Pipeline failed"

### Testnet Deployment (Blue/Orange)

**Triggers:** Testnet deployment job  
**Message:**

- 🚀 Deployment SUCCESS or ⚠️ Deployment FAILED
- Commit SHA and tag
- Deployment status

## What Does NOT Get Notified

- ❌ Feature branch commits (reduces noise)
- ❌ Pull request builds (use GitHub PR interface)
- ❌ Non-critical warnings
- ❌ Individual test results (use logs)

## Channel Recommendations

### Private Channel: `#qfs-ci`

**Purpose:** Internal team notifications  
**Notifications:**

- All pipeline results (success/failure)
- Testnet deployments
- Critical alerts

### Public Channel: `#status` (Optional, future)

**Purpose:** Public transparency  
**Notifications:**

- Testnet deployment success
- Major releases
- Sanitized status updates only

## Local Usage

Developers can send notifications from local pipeline runs:

```bash
# Run pipeline with Discord notifications
export DISCORD_WEBHOOK_URL="your-webhook-url"
python run_pipeline.py

# Or manually notify
python notify_discord.py --type success --commit $(git rev-parse HEAD) --branch $(git branch --show-current)
```

## Benefits

✅ **Immediate visibility** - Know pipeline status instantly  
✅ **No alert fatigue** - Only critical events on important branches  
✅ **ChatOps ready** - Discord as operational status surface  
✅ **Non-intrusive** - Not a system dependency, just notifications  
✅ **Team coordination** - Everyone sees same status

## Troubleshooting

**No notifications received:**

1. Check webhook URL is correct
2. Verify `DISCORD_WEBHOOK_URL` secret is set in GitHub
3. Check Discord channel permissions
4. Look for errors in GitHub Actions logs

**Too many notifications:**

- Notifications only fire on `main`, `release/*`, and tags
- Feature branches are intentionally excluded
- Adjust triggers in `.github/workflows/stage_12_1_pipeline.yml` if needed

## Security Notes

- Webhook URL is a secret - never commit it
- Private channel recommended for internal use
- Public channel should only show sanitized info
- No sensitive data in notifications (commit SHAs are public)

## Future Enhancements

- Add reaction-based commands (👍 to approve deployment)
- Thread replies with detailed logs
- Public status channel for transparency
- Integration with Discord bot for richer interactions
