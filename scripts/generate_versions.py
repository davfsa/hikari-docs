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
"""Generate a `versions.js` file from the contents of `docs/`.

The file will export `availableVersions`, which is an ordered dictionary (newest first)
of version to metadata and `latestStable`, which will contain the latest stable version.

Vesion Metadata keys
--------------------
- p? : Denotes the version as a pre-release.

? = Optional
"""
import json
import pathlib

import hikari_version

INGNORED_VERSIONS = {"master", "stable", "latest"}


docs_path = pathlib.Path.cwd() / "docs"

if not docs_path.exists():
    raise RuntimeError(f"{str(docs_path)!r} does not exist!")
if not docs_path.is_dir():
    raise RuntimeError(f"{str(docs_path)!r} is not a directory!")


available_versions = {}
latest_stable = None

for path in docs_path.iterdir():
    version = path.name

    if not path.is_dir() or version in INGNORED_VERSIONS:
        continue

    metadata = {}

    version = hikari_version.HikariVersion(version)

    if version.prerelease is not None:
        metadata["p"] = 1

    available_versions[version] = metadata

    # If latest_stable is None, replace it
    # If its not None, check that the version we are changing it to is greater and not changing from a stable to a prerelease version
    if latest_stable is None or (
        (version.prerelease is None and latest_stable.prerelease is not None) and version > latest_stable
    ):
        latest_stable = version

if len(available_versions) == 0:
    raise RuntimeError(f"No versions collected! Please ensure {str(docs_path)!r} is not empty")


available_versions = dict(map(lambda x: (str(x[0]), x[1]), sorted(available_versions.items(), reverse=True)))

# Dump
with open(docs_path / "versions.js", "w") as fp:
    fp.write("// This file is generated automatically. Do not manually edit it!\n")
    fp.write(f'const latestStable="{str(latest_stable)}";const availableVersions=')
    json.dump(available_versions, fp, separators=(",", ":"))
