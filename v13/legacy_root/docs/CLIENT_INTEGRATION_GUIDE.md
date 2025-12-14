# Client Integration Guide

This guide explains how clients should interpret and handle AEGIS advisory data and new policy hints from the ATLAS API.

## AEGIS Advisory Fields

AEGIS advisories are included in both feed items and interaction responses. They contain two key fields:

### `block_suggested` (boolean)
- Indicates whether the AEGIS system suggests blocking the content
- This is an advisory flag, not an enforcement directive
- Clients should use this as a strong signal but retain final control

### `severity` (string)
- `"info"` - Normal content with no specific concerns
- `"warning"` - Content that may be inappropriate for some audiences
- `"critical"` - Content with significant safety concerns

## Policy Hints

API responses now include additional policy hints to guide client behavior:

### `visibility_level` (string)
- `"visible"` - Content should be displayed normally
- `"warned"` - Content should be displayed with a warning
- `"hidden"` - Content should be hidden by default (click-through required)

### `warning_banner` (string)
- `"none"` - No warning banner needed
- `"general"` - Generic warning banner
- `"safety"` - Safety-specific warning banner
- `"economic"` - Economic concern warning banner

### `warning_message` (string, optional)
- Human-readable warning message explaining the concern
- May be localized by the client

### `requires_click_through` (boolean)
- Indicates if user must explicitly click through a warning to view content
- Enforcement is client-side for now

### `client_tags` (array of strings)
- Tags to help clients categorize and filter content
- Examples: `["aegis_severity_warning", "aegis_block_suggested"]`

## Client Responsibilities

### Interpretation
1. Always check for `aegis_advisory` in API responses
2. Respect `block_suggested` as a strong recommendation
3. Use `severity` to determine appropriate UI treatment
4. Check for `policy_hints` to get detailed guidance on content presentation

### Enforcement
1. **Client-side only** - No hard server-side deletions or censorship
2. **User control** - Users should retain ultimate control over content visibility
3. **Transparency** - Clearly indicate when content is being filtered based on advisories

### UI Guidelines
1. **Info level** - Display normally with no special treatment
2. **Warning level** - Display with a subtle warning indicator
3. **Critical level** - Hide by default with prominent warning and click-through requirement

## Example Implementation

```javascript
// Pseudo-code for handling feed items with policy hints
function renderFeedItem(item) {
  const advisory = item.aegis_advisory;
  const policyHints = item.policy_hints;
  
  if (!advisory) {
    // No advisory, display normally
    return renderNormalItem(item);
  }
  
  // Use policy hints if available, fall back to manual interpretation
  if (policyHints) {
    switch (policyHints.visibility_level) {
      case "hidden":
        return renderHiddenItem(item, {
          warningMessage: policyHints.warning_message || "Content hidden for safety reasons",
          requiresClickThrough: policyHints.requires_click_through
        });
      case "warned":
        return renderWarnedItem(item, {
          warningMessage: policyHints.warning_message || "This content may be inappropriate",
          requiresClickThrough: policyHints.requires_click_through
        });
      default: // visible
        return renderNormalItem(item);
    }
  } else {
    // Fallback to manual interpretation based on advisory
    switch (advisory.severity) {
      case "critical":
        if (advisory.block_suggested) {
          return renderHiddenItem(item, {
            warningMessage: "This content has been flagged for safety concerns",
            requiresClickThrough: true
          });
        }
        // Fall through to warning if not blocked
      case "warning":
        return renderWarnedItem(item, {
          warningMessage: "This content may be inappropriate for some audiences",
          requiresClickThrough: false
        });
      default: // info or unknown
        return renderNormalItem(item);
    }
  }
}
```

## Preview Endpoint (Coming Soon)

A preview endpoint will be available for testing policy configurations:

```
POST /api/v1/policy/preview
{
  "aegis_advisory": {
    "block_suggested": true,
    "severity": "warning"
  },
  "config": {
    "warning_visibility": "visible"
  }
}

Response:
{
  "policy_hints": {
    "visibility_level": "visible",
    "warning_banner": "general",
    "warning_message": "This content may be inappropriate for some audiences",
    "requires_click_through": false,
    "client_tags": ["aegis_severity_warning", "aegis_block_suggested"]
  }
}
```

This allows operators and AGI systems to experiment with policies without affecting live traffic.