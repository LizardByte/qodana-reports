function showReports(type) {
    let reports = document.getElementsByClassName(`pull-${type}`);

    for (let i = 0; i < reports.length; i++) {
        // remove class "d-none" from each element
        reports[i].classList.remove("d-none");
    }

    // change button
    let button = document.getElementById(`show-${type}`);

    // change on click attribute
    button.setAttribute("onclick", `hideReports('${type}')`);

    button.textContent = `Hide closed ${type}`;
}

function hideReports(type) {
    let reports = document.getElementsByClassName(`pull-${type}`);

    for (let i = 0; i < reports.length; i++) {
        // remove class "d-none" from each element
        reports[i].classList.add("d-none");
    }

    // change button
    let button = document.getElementById(`show-${type}`);

    // change on click attribute
    button.setAttribute("onclick", `showReports('${type}')`);

    button.textContent = `Show closed ${type}`;
}
