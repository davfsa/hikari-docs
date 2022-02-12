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
if [ -z ${COMMIT_MESSAGE+x} ]; then echo '$COMMIT_MESSAGE environment variable is missing' && exit 1; fi
if [ -z "${COMMIT_MESSAGE}" ]; then echo '$COMMIT_MESSAGE environment variable is empty' && exit 1; fi

echo "-- Generating versions.js --"
python scripts/generate_versions.py

echo "-- Updating symbolic links --"
python scripts/update_symlinks.py "${VERSION}"

echo "===== PUSHING CHANGES ====="
git add -Av .
git commit -am "${COMMIT_MESSAGE}"
git push
