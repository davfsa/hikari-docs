# -*- coding: utf-8 -*-
# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021 davfsa
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
import shutil
import subprocess
import time
import typing

import nox

_NoxCallbackSig = typing.Callable[[nox.sessions.Session], None]

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


def nox_session(
    *, only_if: typing.Callable[[], bool] = lambda: True, reuse_venv: bool = False, **kwargs: typing.Any
) -> typing.Callable[[_NoxCallbackSig], typing.Union[_NoxCallbackSig, nox.sessions.Session]]:
    def decorator(func: _NoxCallbackSig) -> typing.Union[_NoxCallbackSig, nox.sessions.Session]:
        func.__name__ = func.__name__.replace("_", "-")

        return nox.session(reuse_venv=reuse_venv, **kwargs)(func) if only_if() else func

    return decorator


@nox_session(reuse_venv=True, venv_backend="none")
def remove_trailing_whitespaces(session: nox.Session) -> None:
    """Check for trailing whitespaces in the project."""
    _remove_trailing_whitespaces(session)


@nox_session(reuse_venv=True, venv_backend="none")
def check_trailing_whitespaces(session: nox.Session) -> None:
    """Check for trailing whitespaces in the project."""
    _remove_trailing_whitespaces(session, check_only=True)


def _remove_trailing_whitespaces(session: nox.Session, check_only: bool = False) -> None:
    count = 0
    total = 0

    start = time.perf_counter()
    for path in REFORMATTING_PATHS:
        if os.path.isfile(path):
            total += 1
            count += remove_trailing_whitespaces_for_file(path, session, check_only)

        for root, dirs, files in os.walk(path, topdown=True, followlinks=False):
            for file in files:
                if file.casefold().endswith(REFORMATTING_FILE_EXTS):
                    total += 1
                    count += remove_trailing_whitespaces_for_file(os.path.join(root, file), session, check_only)

                i = len(dirs) - 1
                while i >= 0:
                    if dirs[i] == "__pycache__":
                        del dirs[i]
                    i -= 1

    end = time.perf_counter()

    remark = "Good job! " if not count else ""
    message = "Had to fix" if not check_only else "Found issues in"
    session.log(
        f"{message} {count} file(s). "
        f"{remark}Took {1_000 * (end - start):.2f}ms to check {total} files in this project.",
    )

    if check_only and count:
        session.error("Trailing whitespaces found. Try running 'nox -s reformat-code' to fix them")


def remove_trailing_whitespaces_for_file(file: str, session: nox.Session, check_only: bool) -> bool:
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
            session.log(f"Trailing whitespaces found in {file}")
            return True

        session.log(f"Removing trailing whitespaces present in {file}")

        with open(file, "wb") as fp:
            fp.writelines(new_lines)

        git = shutil.which("git")
        if git is not None:
            result = subprocess.check_call(
                [git, "add", file, "-vf"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=None,
            )
            assert result == 0, f"`git add {file} -v' exited with code {result}"

        return True
    except Exception as ex:
        print("Failed to check", file, "because", type(ex).__name__, ex)
        return False
