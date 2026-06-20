#!/usr/bin/env bash
# Smoke tests for the house-rules hooks. Run from any directory.
# Each test feeds JSON to the hook on stdin and asserts the output.
set -u

HOOKS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
pass=0; fail=0
chk() {
  if [ "$1" = "$2" ]; then
    pass=$((pass+1))
    echo "PASS: $3"
  else
    fail=$((fail+1))
    echo "FAIL: $3 (expected '$1' got '$2')"
  fi
}

# --- strip-claude-coauthor ---------------------------------------------------

out=$(printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m \\"x\\\\n\\\\nCo-Authored-By: Claude <c@anthropic>\\""}}' \
  | python3 "$HOOKS/strip-claude-coauthor.py")
echo "$out" | grep -q '"permissionDecision": "deny"' \
  && chk yes yes "coauthor trailer denied" \
  || chk yes no  "coauthor trailer denied"

out=$(printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m \\"x\\\\n\\\\nCo-Authored-By: claude.com <x@y>\\""}}' \
  | python3 "$HOOKS/strip-claude-coauthor.py")
echo "$out" | grep -q '"permissionDecision": "deny"' \
  && chk yes yes "coauthor claude.com denied" \
  || chk yes no  "coauthor claude.com denied"

out=$(printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m \\"fix bug\\""}}' \
  | python3 "$HOOKS/strip-claude-coauthor.py")
chk "" "$out" "clean commit silent"

out=$(printf '{"tool_name":"Bash","tool_input":{"command":"ls"}}' \
  | python3 "$HOOKS/strip-claude-coauthor.py")
chk "" "$out" "non-git command silent"

# --- gate-git-write-ops ------------------------------------------------------

TF=$(mktemp); printf '{"role":"user","content":"please refactor"}\n' > "$TF"
out=$(printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m foo"},"transcript_path":"%s"}' "$TF" \
  | python3 "$HOOKS/gate-git-write-ops.py")
echo "$out" | grep -q '"permissionDecision": "ask"' \
  && chk yes yes "gate asks when user did not authorize" \
  || chk yes no  "gate asks when user did not authorize"
rm "$TF"

TF=$(mktemp); printf '{"role":"user","content":"commit and push"}\n' > "$TF"
out=$(printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m foo"},"transcript_path":"%s"}' "$TF" \
  | python3 "$HOOKS/gate-git-write-ops.py")
chk "" "$out" "gate silent on user-authorized commit"
rm "$TF"

TF=$(mktemp); printf '{"role":"user","content":"please refactor"}\n' > "$TF"
out=$(printf '{"tool_name":"Bash","tool_input":{"command":"git push origin master"},"transcript_path":"%s"}' "$TF" \
  | python3 "$HOOKS/gate-git-write-ops.py")
echo "$out" | grep -q '"permissionDecision": "ask"' \
  && chk yes yes "gate covers push" \
  || chk yes no  "gate covers push"
rm "$TF"

out=$(printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m foo"}}' \
  | python3 "$HOOKS/gate-git-write-ops.py")
echo "$out" | grep -q '"permissionDecision": "ask"' \
  && chk yes yes "gate asks when transcript missing" \
  || chk yes no  "gate asks when transcript missing"

out=$(printf '{"tool_name":"Bash","tool_input":{"command":"ls /tmp"}}' \
  | python3 "$HOOKS/gate-git-write-ops.py")
chk "" "$out" "gate silent on non-git command"

# Latest-user-turn (not first) is what authorizes
TF=$(mktemp)
printf '{"role":"user","content":"start working"}\n' >> "$TF"
printf '{"role":"assistant","content":"ok"}\n' >> "$TF"
printf '{"role":"user","content":"go ahead and commit"}\n' >> "$TF"
out=$(printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m foo"},"transcript_path":"%s"}' "$TF" \
  | python3 "$HOOKS/gate-git-write-ops.py")
chk "" "$out" "gate uses latest user turn"
rm "$TF"

# --- flag-pattern-comments --------------------------------------------------

out=$(printf '{"tool_name":"Edit","tool_input":{"new_string":"// pattern: FCIS\\nfn x() {}"}}\n' \
  | python3 "$HOOKS/flag-pattern-comments.py")
echo "$out" | grep -q 'annotation comments' \
  && chk yes yes "pattern: warn" \
  || chk yes no  "pattern: warn"

out=$(printf '{"tool_name":"Edit","tool_input":{"new_string":"# note: added for ticket-123\\ndef x(): pass"}}\n' \
  | python3 "$HOOKS/flag-pattern-comments.py")
echo "$out" | grep -q 'annotation comments' \
  && chk yes yes "note: warn (python)" \
  || chk yes no  "note: warn (python)"

out=$(printf '{"tool_name":"Edit","tool_input":{"new_string":"fn x() { let y = 1; // pattern: not at line start\\n}"}}\n' \
  | python3 "$HOOKS/flag-pattern-comments.py")
chk "" "$out" "inline pattern: not flagged"

out=$(printf '{"tool_name":"Bash","tool_input":{"command":"echo hi"}}\n' \
  | python3 "$HOOKS/flag-pattern-comments.py")
chk "" "$out" "non-edit tool silent"

echo ""
echo "=== Total: $pass passed, $fail failed ==="
[ $fail -eq 0 ]
