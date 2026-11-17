#!/usr/bin/env bash
# Carpet 規則(含 TIS Addition)存在 world/carpet.conf,不在 config/ 資料夾，所以另外用這支腳本跟 repo 同步。
#
#   ./carpet-sync.sh push   把 repo 的 carpet.conf 用 /carpet setDefault 套用到生存服和鏡像服(立即生效，免重啟)
#   ./carpet-sync.sh pull   遊戲內用 /carpet setDefault 改過規則後，把生存服的 carpet.conf 抄回 repo,再 commit
#   ./carpet-sync.sh diff   比較 repo 和生存服目前的 carpet.conf
#
# 注意:push 只會新增/修改規則，不會把 repo 裡刪掉的規則改回預設;要移除請在遊戲內 /carpet removeDefault <規則>。
set -euo pipefail
cd "$(dirname "$0")"

REPO_CONF=carpet.conf
LIVE_CONF=data/world/carpet.conf

rules() { grep -vE '^\s*(#|$)' "$1" | grep -viE '^\s*locked\s*$' || true; }

case "${1:-}" in
  push)
    for c in mc-techsmp mc-techsmp-mirror; do
      if ! docker ps -q -f name="^${c}$" | grep -q .; then echo "skip $c (not running)"; continue; fi
      rules "$REPO_CONF" | while read -r rule value; do
        echo "[$c] carpet setDefault $rule $value"
        docker exec "$c" rcon-cli "carpet setDefault $rule $value"
      done
    done
    ;;
  pull)
    cp "$LIVE_CONF" "$REPO_CONF"
    echo "copied $LIVE_CONF -> $REPO_CONF"
    git --no-pager diff --stat -- "$REPO_CONF" || true
    ;;
  diff)
    diff -u "$REPO_CONF" "$LIVE_CONF" && echo "same"
    ;;
  *)
    sed -n '2,9p' "$0"; exit 1
    ;;
esac
