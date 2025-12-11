#!/usr/bin/env bash

die() {
    echo "*** ${@}"
    exit 1
}

root=$(dirname --  "$(readlink -f ${BASH_SOURCE[0]})")
[[ -z "${root}" || "${root}" = "." ]] && root="${PWD}"
echo "-- root: ${root}"

[[ -d "${root}/venv" ]] && die "${root}/venv directory already exists"

python=$(command -v python3)
[[ -x "${python}" ]] || die "python3 not found"

echo "-- creating ${root}/venv using ${python}"
${python} -m venv "${root}/venv"

echo "-- activating ${root}/venv"
source "${root}/venv/bin/activate"

echo "-- installing into ${root}/venv"
pip3 install -U pip > "${root}/install.log" || die "failed to update pip"
pip3 install -r "${root}/requirements.txt" >> "${root}/install.log" || die "failed to install requirements"
echo "-- finished (see ${root}/install.log for details)"

echo "-- creating ghstats link"
cd "${root}" || die "failed to cd into '${root}'"
[[ -x ghstats ]] || ln -s run.sh ghstats
