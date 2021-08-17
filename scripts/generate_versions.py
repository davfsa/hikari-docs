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

Version Metadata keys
--------------------
- p? : Denotes the version as a pre-release.

? = Optional
"""
import json
import pathlib

import hikari_version

IGNORED_VERSIONS = {"master", "stable", "latest"}


docs_path = pathlib.Path.cwd() / "docs"

if not docs_path.exists():
    raise RuntimeError(f"{str(docs_path)!r} does not exist!")
if not docs_path.is_dir():
    raise RuntimeError(f"{str(docs_path)!r} is not a directory!")


available_versions = {}

for path in docs_path.iterdir():
    version = path.name

    if not path.is_dir() or version in IGNORED_VERSIONS:
        continue

    metadata = {}

    version = hikari_version.HikariVersion(version)

    if version.prerelease is not None:
        metadata["p"] = 1

    available_versions[version] = metadata


if len(available_versions) == 0:
    raise RuntimeError(
        f"No versions collected! Please ensure {str(docs_path)!r} is not empty"
    )


available_versions = dict(
    map(lambda x: (str(x[0]), x[1]), sorted(available_versions.items(), reverse=True))
)

latest_stable = None
# We go back the available versions until we find a non-prerelease one, or the latest pre-release
for v, meta in available_versions.items():
    if "p" not in meta:
        latest_stable = v
        break

else:
    latest_stable = next(iter(available_versions.keys()))

# Dump
file_path = docs_path / "version_switcher.js"
with open(file_path) as fp:
    lines = fp.readlines()

start_index = lines.index("// version_info: start\n") + 1
end_index = lines.index("// version_info: end\n")

if start_index == 0:  # We added 1 to it before
    raise RuntimeError("Missing opening '// version_info: start'")
if end_index == -1:
    raise RuntimeError("Missing closing '// version_info: end'")


lines[start_index:end_index] = [
    f'const latestStable="{str(latest_stable)}";const availableVersions=',
    json.dumps(available_versions, separators=(",", ":")),
    ";\n",
]

with open(file_path, "w") as fp:
    fp.writelines(lines)
