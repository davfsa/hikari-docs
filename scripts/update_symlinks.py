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
import os
import pathlib
import sys

import hikari_version

# Arguments:
# 1. The version to check
_, raw_version = sys.argv

if raw_version == "master":
    print("No symbolic links need to be updated")
    exit()

try:
    version = hikari_version.HikariVersion(raw_version)
except ValueError:
    raise ValueError(f"Invalid hikari version: {raw_version!r}") from None


def create_symlink(
    path: pathlib.Path, name: str, v: hikari_version.HikariVersion
) -> None:
    dst = path / name

    raw_version_link = dst.resolve().name

    if raw_version_link != "master":
        try:
            version_link = hikari_version.HikariVersion(raw_version_link)
        except ValueError:
            raise ValueError(
                f"Invalid hikari version in link: '{dst.resolve()!s}'"
            ) from None

        if version_link > v:
            print(
                f"Not re-creating link of {dst!s} as it already points to a newer version"
            )
            return

    os.remove(dst)
    os.symlink(str(v), dst)
    print(f"{dst!s} -> {v}")


docs_path = pathlib.Path.cwd() / "docs"

create_symlink(docs_path, "latest", version)

if version.prerelease is None:
    create_symlink(docs_path, "stable", version)
