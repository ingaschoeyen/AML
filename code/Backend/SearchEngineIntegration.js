// SearchEngineIntegration.js

'use strict';

const assert = require('assert');
const python = require('python-bridge');

const py = python();

const {
    ex,
    end,
} = py;

ex`import SearchEngine`

const contentField = document.getElementById('searchResultsContent');



function getItemContent(idx){
    // retrieve content of archive item with idx
    let itemContent = dict();
    // retrieve title, description, and metadata of item in data json at idx and store in itemContent
    data = null; // retrieve data json from backend !!! TBD !!!
    let itemData = data[idx];
    itemContent.title = itemData.title;
    itemContent.description = itemData.description;
    return itemContent;
}


function generateContentCard(itemContent){
    // generates HTML for a content card based on itemContent
    // itemContent should contain title, description, and other relevant information about the archive item
    let contentCardHTML = `
        <div class="content-card">
            <h3>${itemContent.title}</h3>
            <p>${itemContent.description}</p>
            <!-- Add more fields as necessary -->
        </div>
    `;
    return contentCardHTML;
}

function generateContentHTML(searchResults){
    let contentHTML = '';
    for (i=0;i<searchResults.length;i++){
        let itemContent = getItemContent(searchResults[i]);
        contentHTML += generateContentCard(itemContent);
    }
    return contentHTML;

}

async function search(){
    let keywords = document.getElementByID('searchKeywords');
    let filters = document.getElementById('searchFilters');
    try {
        // returns idxs of archive items?
        let searchResults = await py`SearchEngine.search(${keywords, filters})`;
        // alternative python call that looks into 
        let contentHTML = generateContentHTML(searchResults);
        contentField.innerHTML = contentHTML;
    } catch (e){
        console.log(e)
    }
    end();

}