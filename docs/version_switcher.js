const masterTreeUrl = "https://api.github.com/repos/davfsa/hikari-docs/git/trees/master";
const specialVersions = ["stable", "latest", "master"]
const versionSelector = document.getElementById("version-selector");


function performRequest(url, handler) {
    let xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.onload = handler;
    xhr.send(null);
}

function docsTreeRequestHandler() {
    if (this.status !== 200) {
        console.error("Something went wrong when loading the 'docs' tree. If this issue persists, please open an issue");
        return;
    }

    let availableVersions = specialVersions;
    JSON.parse(this.responseText)
        .tree
        .filter(function (t) { return (t.type === "tree" && !availableVersions.includes(t.path)); })
        .reverse()
        .forEach(function (t) { availableVersions.push(t.path); });

    versionSelector.innerHTML = "";

    availableVersions.forEach(function (v) {
        let option = document.createElement("option");

        option.value = v;
        option.innerHTML = v;
        versionSelector.appendChild(option);
    });

    // FIXME: Set to 1 when deplying to hikari-py.dev
    versionSelector.value = window.location.pathname.split("/")[2];
    versionSelector.removeAttribute("disabled");
}

function masterTreeRequestHandler() {
    if (this.status !== 200) {
        console.error("Something went wrong when loading the 'master' tree. If this issue persists, please open an issue");
        return;
    }

    let docsTreeUrl = JSON.parse(this.responseText).tree.filter(function (t) { return t.path === "docs" })[0].url;
    performRequest(docsTreeUrl, docsTreeRequestHandler);
}

versionSelector.addEventListener("change", function () {
    // FIXME: Remove when actually deploying to hikari-py.dev. Also, re-add the CNAME
    window.location.href = "/hikari-docs/" + versionSelector.value;
}, { passive: true });

performRequest(masterTreeUrl, masterTreeRequestHandler);
