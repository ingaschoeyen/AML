# Plan for how the search engine works

The search function is implemented in python, in SearchEngine.py, while the retrieval and formatting of the search results is implemented in Javascript, in SearchEngineIntegration.js.


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

