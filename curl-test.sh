#!/usr/bin/env bash
#
# curl-test.sh — end-to-end test of the timeline_post API.
#
# Flow:
#   1. POST a randomly-generated timeline post
#   2. GET all posts and confirm the new one is present
#   3. DELETE the test post (cleanup) and confirm it is gone   [bonus]
#
# Requires: curl, python3 (for JSON parsing). The Flask app must be running.
# Override the target with:  BASE_URL=http://host:port ./curl-test.sh
#
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:5000}"
ENDPOINT="$BASE_URL/api/timeline_post"

# --- Generate random test data ---------------------------------------------
RAND="$RANDOM"
NAME="Test User $RAND"
EMAIL="test$RAND@example.com"
CONTENT="Automated test post $RAND"

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1" >&2; exit 1; }

# --- 1. POST ---------------------------------------------------------------
echo "==> POST $ENDPOINT"
POST_RESPONSE="$(curl -s -X POST "$ENDPOINT" \
  --data-urlencode "name=$NAME" \
  --data-urlencode "email=$EMAIL" \
  --data-urlencode "content=$CONTENT")"
echo "    response: $POST_RESPONSE"

POST_ID="$(printf '%s' "$POST_RESPONSE" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")" \
  || fail "could not parse id from POST response"
echo "    created post id: $POST_ID"

# --- 2. GET + verify present -----------------------------------------------
echo "==> GET $ENDPOINT (verify post is present)"
GET_RESPONSE="$(curl -s "$ENDPOINT")"

if printf '%s' "$GET_RESPONSE" | EXPECTED_ID="$POST_ID" EXPECTED_CONTENT="$CONTENT" python3 -c "
import sys, json, os
posts = json.load(sys.stdin)['timeline_posts']
eid = int(os.environ['EXPECTED_ID'])
ec = os.environ['EXPECTED_CONTENT']
sys.exit(0 if any(p['id'] == eid and p['content'] == ec for p in posts) else 1)
"; then
  pass "post $POST_ID found in GET response"
else
  fail "post $POST_ID not found in GET response"
fi

# --- 3. DELETE + verify gone (bonus) ---------------------------------------
echo "==> DELETE $ENDPOINT/$POST_ID (cleanup)"
DELETE_RESPONSE="$(curl -s -X DELETE "$ENDPOINT/$POST_ID")"
echo "    response: $DELETE_RESPONSE"

echo "==> GET $ENDPOINT (verify post is gone)"
GET_AFTER="$(curl -s "$ENDPOINT")"

if printf '%s' "$GET_AFTER" | EXPECTED_ID="$POST_ID" python3 -c "
import sys, json, os
posts = json.load(sys.stdin)['timeline_posts']
eid = int(os.environ['EXPECTED_ID'])
sys.exit(1 if any(p['id'] == eid for p in posts) else 0)
"; then
  pass "post $POST_ID successfully deleted"
else
  fail "post $POST_ID still present after delete"
fi

echo "All tests passed."
