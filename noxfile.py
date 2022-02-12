# -*- coding: utf-8 -*-
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
"""Code-style jobs."""
import os
import pathlib
import shutil
import subprocess
import time
import typing

import nox

_NoxCallbackSig = typing.Callable[[nox.sessions.Session], None]

GIT = shutil.which("git")
REFORMATTING_FILE_EXTS = (
    ".py",
    ".pyx",
    ".pyi",
    ".c",
    ".cpp",
    ".cxx",
    ".hpp",
    ".hxx",
    ".h",
    ".yml",
    ".yaml",
    ".html",
    ".htm",
    ".js",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".css",
    ".md",
    ".dockerfile",
    "Dockerfile",
    ".editorconfig",
    ".gitattributes",
    ".json",
    ".gitignore",
    ".dockerignore",
    ".flake8",
    ".txt",
    ".sh",
    ".bat",
    ".ps1",
    ".rb",
    ".pl",
)
REFORMATTING_PATHS = (
    *(f for f in os.listdir(".") if os.path.isfile(f) and f.endswith(REFORMATTING_FILE_EXTS)),
    ".github",
    "docs",
    "scripts",
)
IGNORED_PATHS = ("versions.js",)


def nox_session(
    *, reuse_venv: bool = False, **kwargs: typing.Any
) -> typing.Callable[[_NoxCallbackSig], typing.Union[_NoxCallbackSig, nox.sessions.Session]]:
    def decorator(func: _NoxCallbackSig) -> typing.Union[_NoxCallbackSig, nox.sessions.Session]:
        func.__name__ = func.__name__.replace("_", "-")

        return nox.session(reuse_venv=reuse_venv, **kwargs)(func)

    return decorator


@nox_session(reuse_venv=True, venv_backend="none")
def remove_trailing_whitespaces(session: nox.sessions.Session) -> None:
    """Check for trailing whitespaces in the project."""
    _remove_trailing_whitespaces(session)


@nox_session(reuse_venv=True, venv_backend="none")
def check_trailing_whitespaces(session: nox.sessions.Session) -> None:
    """Check for trailing whitespaces in the project."""
    _remove_trailing_whitespaces(session, check_only=True)


def _remove_trailing_whitespaces(session: nox.sessions.Session, check_only: bool = False) -> None:
    session.log(f"Searching for stray trailing whitespaces in files ending in {REFORMATTING_FILE_EXTS}")

    count = 0
    total = 0

    start = time.perf_counter()
    for raw_path in REFORMATTING_PATHS:
        path = pathlib.Path(raw_path)

        dir_total, dir_count = _remove_trailing_whitespaces_for_directory(pathlib.Path(path), session, check_only)

        total += dir_total
        count += dir_count

    end = time.perf_counter()

    remark = "Good job! " if not count else ""
    message = "Had to fix" if not check_only else "Found issues in"
    call = session.error if check_only and count else session.log

    call(
        f"{message} {count} file(s). "
        f"{remark}Took {1_000 * (end - start):.2f}ms to check {total} files in this project."
        + ("\nTry running 'nox -s reformat-code' to fix them" if check_only and count else ""),
    )


def _remove_trailing_whitespaces_for_directory(
    root_path: pathlib.Path, session: nox.sessions.Session, check_only: bool
) -> typing.Tuple[int, int]:
    total = 0
    count = 0

    for path in root_path.glob("*"):
        if path.name.endswith(IGNORED_PATHS):
            continue

        if path.is_file():
            if path.name.casefold().endswith(REFORMATTING_FILE_EXTS):
                total += 1
                count += _remove_trailing_whitespaces_for_file(str(path), session, check_only)
            continue

        dir_total, dir_count = _remove_trailing_whitespaces_for_directory(path, session, check_only)

        total += dir_total
        count += dir_count

    return total, count


def _remove_trailing_whitespaces_for_file(file: str, session: nox.sessions.Session, check_only: bool) -> bool:
    try:
        with open(file, "rb") as fp:
            lines = fp.readlines()
            new_lines = lines[:]

        for i in range(len(new_lines)):
            line = lines[i].rstrip(b"\n\r \t")
            line += b"\n"
            new_lines[i] = line

        if lines == new_lines:
            return False

        if check_only:
            session.warn(f"Trailing whitespaces found in {file}")
            return True

        session.log(f"Removing trailing whitespaces present in {file}")

        with open(file, "wb") as fp:
            fp.writelines(new_lines)

        if GIT is not None:
            result = subprocess.check_call(
                [GIT, "add", file, "-vf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=None
            )
            assert result == 0, f"`git add {file} -v' exited with code {result}"

        return True
    except Exception as ex:
        print("Failed to check", file, "because", type(ex).__name__, ex)
        return True
