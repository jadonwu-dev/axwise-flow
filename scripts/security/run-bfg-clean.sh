#!/usr/bin/env bash
set -euo pipefail
set -f

# This script creates a fresh mirror of AxWise-GmbH/axwise-flow-oss,
# runs BFG Repo-Cleaner with robust secret patterns, force-pushes the
# cleaned history, and verifies the head state with a targeted grep.

ROOT_DIR="$(pwd)"
WORK_DIR="/Users/admin/Downloads"
BFG_JAR="$WORK_DIR/bfg-repo-cleaner-1.14.0.jar"
REPL_FILE="$WORK_DIR/bfg-replacements-axwise.txt"
MIRROR_DIR="$WORK_DIR/axwise-flow-oss-mirror.git"
VERIFY_DIR="$WORK_DIR/axwise-flow-oss-verify"
REPO_URL="https://github.com/AxWise-GmbH/axwise-flow-oss.git"

mkdir -p "$WORK_DIR"

# 1) Create replacements file (minimal, robust patterns)
rm -f "$REPL_FILE"
cat > "$REPL_FILE" << 'EOF'
# BFG replacement rules (minimal, robust)
regex:(?i)AIza[-_A-Za-z0-9]{20,}==>AIzaREDACTED
regex:(?i)(pk_live|pk_test)_[A-Za-z0-9]{10,}==>pk_REDACTED
regex:(?i)(sk_live|sk_test)_[A-Za-z0-9]{10,}==>sk_REDACTED
regex:(?i)whsec_[A-Za-z0-9]{10,}==>whsec_REDACTED
EOF

# 2) Ensure BFG jar
if [ ! -f "$BFG_JAR" ]; then
  echo "Downloading BFG Repo-Cleaner..."
  curl -L -o "$BFG_JAR" \
    https://repo1.maven.org/maven2/com/madgag/bfg-repo-cleaner/1.14.0/bfg-repo-cleaner-1.14.0.jar
fi

# 3) Fresh mirror
rm -rf "$MIRROR_DIR"
GIT_TERMINAL_PROMPT=1 git clone --mirror "$REPO_URL" "$MIRROR_DIR"

# 4) Run BFG
pushd "$MIRROR_DIR" >/dev/null
java -jar "$BFG_JAR" --replace-text "$REPL_FILE"

# 5) GC and push
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "Force-pushing cleaned history (you may be prompted to auth)..."
git push --force --mirror
popd >/dev/null

# 6) Verify
rm -rf "$VERIFY_DIR"
git clone "$REPO_URL" "$VERIFY_DIR"
cd "$VERIFY_DIR"

PATTERN='(pk_live|pk_test)_[A-Za-z0-9]{10,}|(sk_live|sk_test)_[A-Za-z0-9]{10,}|whsec_[A-Za-z0-9]{10,}|AIza[-_A-Za-z0-9]{20,}'
echo "Scanning HEAD for sensitive patterns: $PATTERN"
if grep -R -nI -E "$PATTERN" . --exclude-dir=.git --exclude-dir=node_modules; then
  echo "Potential sensitive patterns remain in HEAD" >&2
  exit 1
else
  echo "No sensitive patterns found in HEAD"
fi

echo "Done."

