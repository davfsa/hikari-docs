// Copyright (c) 2020 Nekokatt
// Copyright (c) 2021-present davfsa

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
if (typeof availableVersions === 'undefined') {
    throw "Missing 'availableVersions' variable!";
}
if (typeof latestStable === 'undefined') {
    throw "Missing 'latestStable' variable!";
}
if (typeof currentVersion === 'undefined') {
    throw "Missing 'currentVersion' variable!";
}

const specialVersions = ["stable", "latest", "master"];
const versionSelector = document.getElementById("version-selector");
const versionWarning = document.getElementById("version-warning");

// Add listener
versionSelector.addEventListener("change", function () {
    // FIXME: Set remove `/hikari-docs` when deplying to docs.hikari-py.dev. Also, re-add the CNAME
    window.location.href = `/hikari-docs/${versionSelector.value}`;
}, { passive: true });


// Load in versions
versionSelector.innerHTML = "";

let versions = specialVersions.concat(Object.keys(availableVersions));
versions.forEach(function (v) {
    let option = document.createElement("option");

    option.value = v;
    option.innerText = v;
    versionSelector.appendChild(option);
});


versionSelector.value = currentVersion;
versionSelector.removeAttribute("disabled");

// Display warning if needed
let vIndex = versions.indexOf(versionSelector.value);
let lvIndex = versions.indexOf(latestStable);

if (versionSelector.value === "master") {
    versionWarning.innerText = "Unreleased version!";
} else if (vIndex <= specialVersions.length - 1 || vIndex == lvIndex) {
    versionWarning.innerText = "";
} else if (vIndex < lvIndex) {
    versionWarning.innerText = "Pre-release version!";
} else {
    versionWarning.innerText = "Not latest!";
}
