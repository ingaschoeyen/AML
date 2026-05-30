// pdfViewer.js

let currentPdfObjectUrl = null;

function getPdfViewerElements(viewerId) {
    const viewer = document.getElementById(viewerId);

    if (!viewer) {
        return {};
    }

    return {
        viewer,
        iframe: viewer.querySelector("iframe"),
        status: viewer.querySelector("[data-pdf-status]")
    };
}

function setPdfStatus(statusElement, message, isError = false) {
    if (!statusElement) {
        return;
    }

    statusElement.textContent = message;
    statusElement.dataset.state = isError ? "error" : "ready";
}

function loadPDF(pathToPdf, viewerId = "pdf-viewer-panel") {
    const { viewer, iframe, status } = getPdfViewerElements(viewerId);

    if (!viewer || !iframe) {
        console.warn(`PDF viewer container not found: ${viewerId}`);
        return Promise.resolve(false);
    }

    viewer.open = true;
    viewer.scrollIntoView({ behavior: "smooth", block: "start" });
    setPdfStatus(status, "Loading PDF preview...");

    return fetch(pathToPdf)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to fetch PDF: ${response.status} ${response.statusText}`);
            }

            return response.blob();
        })
        .then(file => {
            if (currentPdfObjectUrl) {
                URL.revokeObjectURL(currentPdfObjectUrl);
            }

            currentPdfObjectUrl = URL.createObjectURL(file);
            iframe.src = currentPdfObjectUrl;
            iframe.setAttribute("title", `PDF preview for ${pathToPdf}`);
            setPdfStatus(status, `Previewing: ${pathToPdf}`);
            return currentPdfObjectUrl;
        })
        .catch(error => {
            if (iframe) {
                iframe.removeAttribute("src");
            }

            setPdfStatus(status, `Unable to load PDF: ${pathToPdf}`, true);
            console.error("PDF load error:", error);
            throw error;
        });
}

function clearPDF(viewerId = "pdf-viewer-panel") {
    const { iframe, status } = getPdfViewerElements(viewerId);

    if (currentPdfObjectUrl) {
        URL.revokeObjectURL(currentPdfObjectUrl);
        currentPdfObjectUrl = null;
    }

    if (iframe) {
        iframe.removeAttribute("src");
    }

    setPdfStatus(status, "No PDF loaded.");
}

window.loadPDF = loadPDF;
window.clearPDF = clearPDF;

