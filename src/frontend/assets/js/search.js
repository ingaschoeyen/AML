// search.js

// Usage: function that gets query from website and sends it to backend search function
// receives list of 

// TODO: 
//      add filters to search query, 
//     add loading spinner while waiting for results,
//     add error handling for failed search requests
//     add function for  loading pdf in page when clicking on search result

let apiURL = "http://localhost:8000/api/search";

function getSelectedFileTypes() {
    const allCheckbox = document.getElementById("file-type-all");
    const optionCheckboxes = Array.from(document.querySelectorAll(".file-type-option"));

    if (allCheckbox && allCheckbox.checked) {
        return ["all"];
    }

    return optionCheckboxes.filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);
}

function setupFileTypeGroup() {
    const allCheckbox = document.getElementById("file-type-all");
    const optionCheckboxes = Array.from(document.querySelectorAll(".file-type-option"));

    if (!allCheckbox || optionCheckboxes.length === 0) return;

    allCheckbox.addEventListener("change", () => {
        if (allCheckbox.checked) {
            optionCheckboxes.forEach(cb => cb.checked = false);
        }
    });

    optionCheckboxes.forEach(cb => cb.addEventListener("change", () => {
        if (cb.checked && allCheckbox.checked) allCheckbox.checked = false;
    }));
}

function getSelectedRadioValue(name, defaultValue) {
    const selectedOption = document.querySelector(`input[name="${name}"]:checked`);
    return selectedOption ? selectedOption.value : defaultValue;
}

function getInputValue(id, defaultValue = "") {
    const element = document.getElementById(id);

    if (!element || element.value === null || element.value === "") {
        return defaultValue;
    }

    return element.value;
}

function getNumberInputValue(id, defaultValue = undefined) {
    const rawValue = getInputValue(id, "");

    if (rawValue === "") {
        return defaultValue;
    }

    const parsedValue = Number(rawValue);
    return Number.isNaN(parsedValue) ? defaultValue : parsedValue;
}

function buildSearchBody(query) {
    const fileTypes = getSelectedFileTypes();
    const selectedFileType = fileTypes.length === 0 || fileTypes.includes("all") ? undefined : fileTypes[0];
    const selectedMode = getSelectedRadioValue("search-type", "semantic");

    const body = {
        query,
        index_dir: "../results/index",
        mode: selectedMode,
        embedding_model: getInputValue("embedding-model-select", "clips/e5-small-trm-nl"),
        file_type: selectedFileType,
        year_from: getNumberInputValue("start-date"),
        year_to: getNumberInputValue("end-date"),
        place_x: getNumberInputValue("longitude"),
        place_y: getNumberInputValue("latitude"),
        place_radius_km: getNumberInputValue("radius", 2.0),
        road: getInputValue("road", undefined),
        hm: getNumberInputValue("hm"),
        hm_radius: getNumberInputValue("hm-radius", 1.0),
        top_k: getNumberInputValue("top-k", 10)
    };

    return Object.fromEntries(
        Object.entries(body).filter(([, value]) => value !== undefined && value !== "")
    );
}

document.addEventListener("DOMContentLoaded", () => {
    setupFileTypeGroup();
});

function createPreviewCard(result) {
    const pdfUrl = typeof toPdfUrl === "function" ? toPdfUrl(result.source_path) : result.source_path;

    let card = document.createElement("div");
    card.className = "result-card";
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", `Preview PDF for ${result.file_name}`);
    card.addEventListener("click", () => {
        loadPDF(pdfUrl);
    });
    card.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            loadPDF(pdfUrl);
        }
    });
    
    let title = document.createElement("h3");
    title.textContent = result.file_name;
    card.appendChild(title);
    
    let snippet = document.createElement("p");
    snippet.textContent = result.snippet;
    card.appendChild(snippet);
    
    let link = document.createElement("a");
    link.href = pdfUrl; // TODO: make this dynamic based on user/session;
    link.textContent = pdfUrl;
    link.target = "_blank";
    card.appendChild(link);

    let viewButton = document.createElement("button");
    viewButton.className = "view-pdf-button";
    viewButton.textContent = "View PDF";
    viewButton.addEventListener("click", event => {
        event.stopPropagation();
    });
    viewButton.addEventListener("click", () => {
        loadPDF(pdfUrl); // TODO: make this dynamic based on user/session;
    });
    card.appendChild(viewButton);

    return card;
}

async function searchRequest(query) {
    const body = buildSearchBody(query);
    console.log("Search request body:", body);
    
    let t_start =  new Date().getTime();
    let response = await fetch(apiURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    });
    let t_end = new Date().getTime();
    console.log(`Search request took ${(t_end - t_start) / 1000} seconds`);
    return response.json();
}

async function search(){
    let query = document.getElementById("search-input").value;
    console.log("Searching for:", query);
    document.getElementById("results-list").innerHTML = "<div class='results-empty'>Loading...</div>";
    //  construct body of API request with filters

    try {
        let data = await searchRequest(query);
        console.log("Search results:", data);
        let resultsDiv = document.getElementById("results-list");
            resultsDiv.innerHTML = "";
            if (!data.results || data.results.length === 0) {
                resultsDiv.innerHTML = "<div class='results-empty'>No results found.</div>";
                return;
            }

            data.results.forEach(result => {
                console.log("processing result:", result.file_name);
                let card = createPreviewCard(result);
                card.className = "result-item result-card";
                resultsDiv.appendChild(card);
            });
        }
    catch (error) {
        console.error("Search error:", error);
        document.getElementById("results-list").innerHTML = "<div class='results-empty'>An error occurred while searching. Please try again.</div>";
    }
}