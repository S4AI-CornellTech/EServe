#!/usr/bin/env bash
# EServe hands-on tutorial runner (see TUTORIAL.md). Self-contained in this repo — wraps tutorial.py.
#   ./tutorial.sh --gpu H100HGX --host
#   ./tutorial.sh --gpu-file exercises/gpu_l4.json --host --grid-ci 30 --util 0.5
#
# Python: set $PYTHON to an interpreter that can import `server_carbon` (this repo's src/) and
# `act_core` (EServe's dependency). Defaults to python3. From the full-stack-carbon suite,
# `make tutorial-eserve` passes the suite's .envs/eserve python.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python3}"
exec "$PY" "$HERE/tutorial.py" "$@"
