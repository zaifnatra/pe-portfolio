#!/bin/bash
# Post a deployment status message to the Discord webhook in $DISCORD_WEBHOOK.
#
# Usage: discord-notify.sh <title> <description>
set -euo pipefail

TITLE="$1"
DESCRIPTION="$2"

if [ -z "${DISCORD_WEBHOOK:-}" ]; then
  echo "DISCORD_WEBHOOK is not set. Add it as a repository secret." >&2
  exit 1
fi

RUN_URL="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"

CONTENT="$(printf '%s\n%s\nCommit: `%s`\nLogs: %s' \
  "$TITLE" "$DESCRIPTION" "${GITHUB_SHA:0:7}" "$RUN_URL")"

# --data-urlencode (rather than a raw -d) so backticks, newlines and any '&' or
# '#' in the message reach Discord intact instead of splitting the form body.
# The content goes in over stdin ("@-") rather than as an argument so it is not
# reshaped by the shell and never shows up in the process list.
printf '%s' "$CONTENT" | curl -sS --fail -X POST \
  --data-urlencode "content@-" \
  "$DISCORD_WEBHOOK"
