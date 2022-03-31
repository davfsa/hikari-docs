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

// Anything enclosed in the 'version_info' comments will be automatically replaced by the deploy script.
// Do not manually edit!
// version_info: start
const latestStable="";const availableVersions={};
// version_info: end

let specialVersions = ["stable", "latest", "master"];
let versionSelector = document.getElementById("version-selector");
let versionWarning = document.getElementById("version-warning");
let currentVersion = window.location.pathname.split("/")[2];

// Add listener
versionSelector.addEventListener("change", function () {
    let mainUrl = `${window.location.origin}/hikari-docs/${versionSelector.value}`;
    let possibleUrl = `${mainUrl}/${window.location.pathname.split("/").slice(3).join("/")}`;

    const http = new XMLHttpRequest();
    // 301 can be caused by Github Pages at times for some reason
    http.onreadystatechange = function () {
        window.location = `${http.status === 200 || http.status === 301 ? possibleUrl : mainUrl}${window.location.hash}`;
    }

    http.open("HEAD", possibleUrl);
    http.send();
}, { passive: true });

// Load in versions
let versionSelectorInnerHTML = "";
let versions = specialVersions.concat(Object.keys(availableVersions));
versions.forEach(function (v) {
    if (v === currentVersion) {
        versionSelectorInnerHTML += `<option value="${v}" selected="selected">${v}</option>`;
    } else {
        versionSelectorInnerHTML += `<option value="${v}">${v}</option>`;
    }
});

versionSelector.innerHTML = versionSelectorInnerHTML;
versionSelector.removeAttribute("disabled");

// Display warning if needed
if (versionSelector.value === "master") {
    versionWarning.innerText = "This documentation is from an unreleased development version. Proceed with caution!";
} else if (versions.indexOf(versionSelector.value) > versions.indexOf(latestStable)) {
    versionWarning.innerHTML = 'This documentation is for an outdated version. Consider upgrading to the <a href="/hikari-docs/stable">latest stable version</a>';
}
