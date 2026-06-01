// pdfViewer.js

let currentPdfObjectUrl = null;
const pdfServerOrigin = "http://localhost:5500";

function buildServerPdfUrl(relativePath) {
    if (!relativePath) {
        return relativePath;
    }

    if (/^https?:\/\//i.test(relativePath)) {
        return relativePath;
    }

    const normalizedPath = relativePath.startsWith("/") ? relativePath : `/${relativePath}`;
    return `${pdfServerOrigin}${normalizedPath}`;
}

function toPdfUrl(pathToPdf) {
    if (!pathToPdf) {
        return pathToPdf;
    }

    if (/^https?:\/\//i.test(pathToPdf)) {
        return pathToPdf;
    }

    const normalizedPath = pathToPdf.replace(/\\/g, "/");
    const publicDataIndex = normalizedPath.indexOf("/public/data/");

    if (publicDataIndex !== -1) {
        return buildServerPdfUrl(`/data/${normalizedPath.slice(publicDataIndex + "/public/data/".length)}`);
    }

    const legacyDataIndex = normalizedPath.indexOf("/src/data/");

    if (legacyDataIndex !== -1) {
        return buildServerPdfUrl(`/data/${normalizedPath.slice(legacyDataIndex + "/src/data/".length)}`);
    }

    if (normalizedPath.startsWith("data/")) {
        return buildServerPdfUrl(`/${normalizedPath}`);
    }

    return buildServerPdfUrl(normalizedPath);
}

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

async function loadPDF(pathToPdf, viewerId = "pdf-viewer-panel") {
    const pdfUrl = toPdfUrl(pathToPdf);
    const { viewer, iframe, status } = getPdfViewerElements(viewerId);

    if (!viewer || !iframe) {
        console.warn(`PDF viewer container not found: ${viewerId}`);
        return Promise.resolve(false);
    }

    viewer.open = true;
    viewer.scrollIntoView({ behavior: "smooth", block: "start" });
    setPdfStatus(status, "Loading PDF preview...");
    try {
        const response = await fetch(pdfUrl);

        if (!response.ok) {
            throw new Error(`Failed to fetch PDF: ${response.status} ${response.statusText}`);
        }

        const file = await response.blob();

        if (currentPdfObjectUrl) {
            URL.revokeObjectURL(currentPdfObjectUrl);
        }

        currentPdfObjectUrl = URL.createObjectURL(file);
        iframe.src = currentPdfObjectUrl;
        iframe.setAttribute("title", `PDF preview for ${pdfUrl}`);
        setPdfStatus(status, `Previewing: ${pdfUrl}`);
        return currentPdfObjectUrl;
    } catch (error) {
        if (iframe) {
            iframe.removeAttribute("src");
        }

        setPdfStatus(status, `Unable to load PDF: ${pdfUrl}`, true);
        console.error("PDF load error:", error);
        throw error;
    }
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
window.toPdfUrl = toPdfUrl;

