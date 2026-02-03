#!/usr/bin/env bash
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

ofa apps up "$SCRIPT_DIR/apps.yml"

NETWORK="${OPENFACTORY_NETWORK:-factory-net}"
docker network inspect "$NETWORK" >/dev/null

# Grab images from apps.yml, then all container IDs built from those images (dedup)
images=$(awk '$1=="image:"{print $2}' "$SCRIPT_DIR/apps.yml")
cids=$(for img in $images; do docker ps -aq --filter "ancestor=$img"; done | sort -u)

# Connect + restart
for cid in $cids; do
  docker network connect "$NETWORK" "$cid" >/dev/null 2>&1 || true
  docker restart "$cid" >/dev/null
done

# Wait until running (+ healthy when healthcheck exists)
timeout="${APPS_WAIT_TIMEOUT:-300}"
deadline=$((SECONDS + timeout))

while (( SECONDS < deadline )); do
  ok=1
  for cid in $cids; do
    running="$(docker inspect -f '{{.State.Running}}' "$cid" 2>/dev/null || echo false)"
    health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}healthy{{end}}' "$cid" 2>/dev/null || echo unknown)"
    if [[ "$running" != "true" || "$health" != "healthy" ]]; then
      ok=0
      break
    fi
  done

  (( ok )) && exit 0
  sleep 2
done

echo "ERROR: Timed out waiting for app containers to be ready." >&2
for cid in $cids; do
  name="$(docker inspect -f '{{.Name}}' "$cid" 2>/dev/null | sed 's|^/||')"
  status="$(docker inspect -f '{{.State.Status}}' "$cid" 2>/dev/null || echo unknown)"
  health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid" 2>/dev/null || echo none)"
  echo " - ${name:-$cid}: status=$status health=$health" >&2
done
exit 1
