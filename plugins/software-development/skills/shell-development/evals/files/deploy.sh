#!/bin/sh
set -eu

targets=("$@")
for target in "${targets[@]}"; do
    [[ -n "$target" ]] && deploy "$target"
done
