#!/usr/bin/env bash
# 把生存服(mc-techsmp)的世界同步到創造鏡像服(mc-techsmp-mirror)。
# 由 cron 每天 05:00 執行，也可以手動跑。鏡像服上的改動會被覆蓋。
set -euo pipefail
cd "$(dirname "$0")"

rcon() { docker exec mc-techsmp rcon-cli "$@"; }

echo "[$(date '+%F %T')] refresh-mirror start"

if ! docker ps -q -f name='^mc-techsmp$' | grep -q .; then
  echo "survival server not running, abort"; exit 1
fi

docker compose stop mirror

# 不管成功或失敗，都一定要把生存服的自動存檔打開
trap 'rcon save-on >/dev/null || echo "WARNING: save-on failed, run it manually!"' EXIT
rcon save-off
rcon "save-all flush"
sleep 5

mkdir -p mirror-data/world
rsync -a --delete --exclude 'session.lock' data/world/ mirror-data/world/

rcon save-on
trap - EXIT

docker compose up -d mirror
echo "[$(date '+%F %T')] refresh-mirror done"
