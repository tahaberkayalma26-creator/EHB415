#!/usr/bin/env bash
set -euo pipefail
arac_dizini="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$arac_dizini/ss_icin_calistir.py"
