#!/usr/bin/env bash
#
# Reset the public demo corpus to the curated baseline. Run hourly via cron so
# the demo self-heals — any document a visitor uploads or deletes is rolled back
# within the hour, and the catalog always shows the same clean set of files.
#
# It only touches the API when the corpus differs from the baseline, so a clean
# hour costs one GET and re-embeds nothing.
#
#   crontab entry:
#   0 * * * * /opt/app/deploy/demo/reset-demo.sh >> /home/ec2-user/demo-reset.log 2>&1
set -euo pipefail

API="${DEMO_API:-http://localhost:8000}"
SEED_DIR="$(cd "$(dirname "$0")" && pwd)"

mapfile -t SEED_FILES < <(ls "$SEED_DIR"/*.md 2>/dev/null | sort)
expected="$(for f in "${SEED_FILES[@]}"; do basename "$f"; done | sort | tr '\n' ',')"

ts="$(date -u +%FT%TZ)"
docs_json="$(curl -sf "$API/documents" 2>/dev/null || echo '[]')"
current="$(printf '%s' "$docs_json" | python3 -c \
  'import sys,json; print(",".join(sorted(x["filename"] for x in json.load(sys.stdin)))+",")' \
  2>/dev/null || echo 'PARSE_ERROR')"

if [ "$current" = "$expected" ]; then
  echo "$ts clean — $current"
  exit 0
fi

# Corpus drifted (a visitor changed it). Wipe and reseed the baseline.
ids="$(printf '%s' "$docs_json" | python3 -c \
  'import sys,json; [print(x["id"]) for x in json.load(sys.stdin)]' 2>/dev/null || true)"
for id in $ids; do
  curl -sf -X DELETE "$API/documents/$id" >/dev/null 2>&1 || true
done
for f in "${SEED_FILES[@]}"; do
  curl -sf -F "file=@$f" -F "collection=default" "$API/documents" >/dev/null 2>&1 || true
done
echo "$ts reseeded — $expected"
