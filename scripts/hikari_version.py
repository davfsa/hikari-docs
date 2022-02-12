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
#
# FIXME: Update with the new link which adds `__hash__`
# Taken from https://github.com/hikari-py/hikari/blob/<TODO>/hikari/internal/ux.py#<TODO>
from __future__ import annotations

import re
import typing

if typing.TYPE_CHECKING:
    CmpTuple = typing.Tuple[int, int, int, typing.Union[int, float]]


_VERSION_REGEX: typing.Final[typing.Pattern[str]] = re.compile(r"^(\d+)\.(\d+)\.(\d+)(\.[a-z]+)?(\d+)?$", re.I)


# This is a modified version of packaging.version.Version to better suit our needs
class HikariVersion:
    """Hikari strict version."""

    __slots__: typing.Sequence[str] = ("version", "prerelease", "_cmp")

    version: typing.Tuple[int, int, int]
    prerelease: typing.Optional[typing.Tuple[str, int]]

    def __init__(self, vstring: str) -> None:
        match = _VERSION_REGEX.match(vstring)
        if not match:
            raise ValueError(f"Invalid version: '{vstring}'")

        (major, minor, patch, prerelease, prerelease_num) = match.group(1, 2, 3, 4, 5)

        self.version = (int(major), int(minor), int(patch))
        self.prerelease = (prerelease, int(prerelease_num) if prerelease_num else 0) if prerelease else None

        prerelease_num = int(prerelease_num) if prerelease else float("inf")
        self._cmp = self.version + (prerelease_num,)

    def __str__(self) -> str:
        vstring = ".".join(map(str, self.version))

        if self.prerelease:
            vstring += "".join(map(str, self.prerelease))

        return vstring

    def __repr__(self) -> str:
        return f"HikariVersion('{str(self)}')"

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: typing.Any) -> bool:
        return self._compare(other, lambda s, o: s == o)

    def __ne__(self, other: typing.Any) -> bool:
        return self._compare(other, lambda s, o: s != o)

    def __lt__(self, other: typing.Any) -> bool:
        return self._compare(other, lambda s, o: s < o)

    def __le__(self, other: typing.Any) -> bool:
        return self._compare(other, lambda s, o: s <= o)

    def __gt__(self, other: typing.Any) -> bool:
        return self._compare(other, lambda s, o: s > o)

    def __ge__(self, other: typing.Any) -> bool:
        return self._compare(other, lambda s, o: s >= o)

    def _compare(self, other: typing.Any, method: typing.Callable[[CmpTuple, CmpTuple], bool]) -> bool:
        if not isinstance(other, HikariVersion):
            return NotImplemented

        return method(self._cmp, other._cmp)
