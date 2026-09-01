#!/usr/bin/env bash
# vim: set noexpandtab tabstop=2:
# Run the whole match->merge pipeline sequentially, for both sides.

source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

for script in "$BASEDIR"/[0-9][0-9]_*.sh; do
	echo "== $(basename "$script")"
	bash "$script"
done
