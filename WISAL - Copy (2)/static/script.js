
function toggleForm() {
    const form = document.getElementById("hepForm");

    if (form.style.display === "none" || form.style.display === "") {
        form.style.display = "block";
    } else {
        form.style.display = "none";
    }
}

function toggleUpdateForm(hepId) {
    const form = document.getElementById("updateForm-" + hepId);

    if (form.style.display === "none" || form.style.display === "") {
        form.style.display = "block";
    } else {
        form.style.display = "none";
    }
}

function toggleSummary() {
    const summary = document.getElementById("summaryContent");
    const weeks = document.getElementById("weeks");
    const form = document.getElementById("summaryForm");

    if (!weeks.value || weeks.value < 1 || weeks.value > 52) {
        weeks.reportValidity();
        return;
    }

    const params = new URLSearchParams(window.location.search);
    const currentWeeks = params.get("weeks");

    if (currentWeeks !== weeks.value) {
        form.requestSubmit();
        return;
    }

    if (summary.style.display === "none") {
        summary.style.display = "block";
    } else {
        summary.style.display = "none";
    }
}