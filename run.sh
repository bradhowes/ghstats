#!/usr/bin/env bash

die() {
    echo "*** ${@}"
    exit 1
}

root=$(dirname --  "$(readlink -f ${BASH_SOURCE[0]})")
[[ -z "${root}" || "${root}" = "." ]] && root="${PWD}"
[[ -d "${root}/venv" ]] || die "${root}/venv directory does not exist - run ${root}/install.sh"
source "${root}/venv/bin/activate"

python3 "${root}/ghstats.py"
