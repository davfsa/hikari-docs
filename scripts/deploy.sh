#!/bin/sh
# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021-present davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
set -e

echo "Defined environment variables"
env | grep -oP "^[^=]+" | sort

if [ -z ${VERSION+x} ]; then echo '$VERSION environment variable is missing' && exit 1; fi
if [ -z "${VERSION}" ]; then echo '$VERSION environment variable is empty' && exit 1; fi
if [ -z ${SUPER_REPO_PATH+x} ]; then echo '$SUPER_REPO_PATH environment variable is missing' && exit 1; fi
if [ -z "${SUPER_REPO_PATH}" ]; then echo '$SUPER_REPO_PATH environment variable is empty' && exit 1; fi
if [ -z ${DOCS_REPO_PATH+x} ]; then echo '$DOCS_REPO_PATH environment variable is missing' && exit 1; fi
if [ -z "${DOCS_REPO_PATH}" ]; then echo '$DOCS_REPO_PATH environment variable is empty' && exit 1; fi

BASE_PATH=$(pwd)

echo "===== TRAVELING TO ${SUPER_REPO_PATH} ====="
cd "${SUPER_REPO_PATH}"

REF="$(git rev-parse HEAD)"

if [ "${VERSION}" == "master" ]; then
  REF_TO_SET="MASTER"
else
  REF_TO_SET="${REF}"
fi

echo "-- Setting __git_sha1__ to '${REF_TO_SET}' --"
sed "/^__git_sha1__.*/, \${s||__git_sha1__: typing.Final[str] = \"${REF_TO_SET}\"|g; b}; \$q1" -i hikari/_about.py || (echo "Variable '__git_sha1__' not found in about!" && exit 1)

rm -rf public
mkdir public

nox -s pdoc
[ ! -d "public/docs" ] && exit 1

echo "===== TRAVELING TO ${BASE_PATH} ====="
cd "${BASE_PATH}"
mv "${SUPER_REPO_PATH}/public/docs" "${DOCS_REPO_PATH}/docs/${VERSION}"

echo "===== TRAVELING TO ${DOCS_REPO_PATH} ====="
cd "${DOCS_REPO_PATH}"

if [ "${VERSION}" == "master" ]; then
  echo "${REF}" > ".master-docs-sha"
fi

echo "-- Updating versions_switcher.js --"
python scripts/generate_versions.py

echo "-- Updating symbolic links --"
python scripts/update_symlinks.py "${VERSION}"

echo "===== PUSHING CHANGES ====="
git add -Av .
git commit -am "Documentation for ${VERSION} [https://github.com/hikari-py/hikari/commit/${REF}]"
git push
