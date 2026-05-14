# Plan for how the search engine works

The search function is implemented in python, in SearchEngine.py, while the retrieval and formatting of the search results is implemented in Javascript, in SearchEngineIntegration.js.


## Search Data Representation

- Images:
    - use structural drawing types in recovered metadata for filters
        - specification drawing (bestekstekening)
        - reinforcement drawing (wapeningstekening)
        - concrete formwork drawing 
        - site plan (situatietekening)
        - steel drawing (staaltekening)
        - detail drawing (detailtekening)  
- Text: 
    - highlight keywords 
- Geographical Data:
    - GeoJSON format for marking location of items
        - cordinates: [longitude, latitude, *elevation]
        - types of objects: (Multi-) Point, LineString, Polygon
    - link to idx of asset that can be used to retrieve the content of the asset



## SearchEngine.py

tbd

## SearchEngineIntegration.js

The SearchEngineIntegration.js file mediates between the frontent and the SearchEngine.py file. It sends the search query to the SearchEngine.py file, retrieves the search results, and then retrieves the content of the archive items corresponding to the search results. Finally, it displays the content of the archive items in the frontend.
It does so in the following chain of functions:

- clicking the search button triggers the search function which queries the contents of the search field and the status of the filter checkboxes, and sends this information to the SearchEngine.py file in a try-catch block and asynchronously
- the SearchEngine.py file returns the idxs of the archive items that match the search query
- the idxs are passed to the generateContentHTML function which generates the HTML content to be displayed in the frontend by passing the idxs to the generateContentCard function
    - the generateContentCard generates a div class='Card' for each indx and fills the div with the content of the archive item corresponding to the idx
    - it calls the getItemContent function to retrieve the content of the archive items corresponding to the idxs 
    - the content is formatted into 
        <div class='Card'>
            <h2>Title</h2>
            <p>Content</p>
        </div>


## Complexity considerations

- retrieve item on demand or load all items at the beginning? 
    - retrieve on demand: faster initial load time, but slower search results
    - load all items at the beginning: slower initial load time, but faster search results
- how to handle large number of search results?
    - pagination: display a limited number of search results per page and provide navigation to move between pages
    - infinite scrolling: load more search results as the user scrolls down the page