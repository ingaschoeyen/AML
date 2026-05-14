#embedding_service.py


from sentence_transformers import SentenceTransformer

from langchain_text_splitters import RecursiveCharacterTextSplitter


import pandas as pd
import numpy as np
import os


"""
Args:

    - model_name: name of the sentence transformer model to use for embedding, recommend 'clips/e5-small-trm-nl' 
    - path_to_text: path to csv file containing text to be embedded, should have columns 'file_id', 'file_name', 'raw_text'


Usage:

TODO:

    - add VisualEmbedder class for visual embedding of images
        - will be used to create embedding for semantic embedder to generate description + metadata

"""
class VisualEmbedder:
    def __init__(self, params):
        self.params = params
        self.model = None # TODO: add visual embedding model
        print("Model loaded")

class SemanticEmbedder:
    def __init__(self, params):
        self.params = params
        self.model = SentenceTransformer(params["model_name"])
        print("Model loaded")
        self.text, df_na = self.load_files(params["path_to_text"])
        print("Files loaded")
        self.na = df_na['file_id'].tolist()

    def load_files(self, path_to_csv) -> pd.DataFrame:
        # load data into pandas dataframe
        df_in = pd.read_csv(path_to_csv)
        print(f"Number of rows in original dataframe: {len(df_in)}")
        # drop na values in text_sep
        df_no_na = df_in.dropna(subset=['raw_text'])
        print(f"Number of rows with raw_text: {len(df_no_na)}")

        # get the dropped rows and return them as a separate dataframe
        df_na = df_in[~df_in.index.isin(df_no_na.index)]
        print(f"Number of rows without raw_text: {len(df_na)}")

        # separate text into list of strings split by new line, then merge into one string per page
        df_no_na['text_sep'] = df_no_na['raw_text'].apply(lambda x: " ".join(str(x).split("\n")))
        # group by file_id and merge text_sep into list of strings
        df_out = df_no_na[['file_id', 'file_name', 'text_sep']].groupby("file_id")["text_sep"].apply(list).reset_index(name="text_sep")
        
        
        return df_out, df_na

    def file_embedding(self, text):
        # merge list of strings from pages into one string and compute embedding for entire file
        return self.model.encode(" ".join(text), convert_to_tensor=True)

    def page_embedding(self, text):
        return [self.model.encode(page, convert_to_tensor=True) for page in text]

    def merge_embeddings(self, embeddings, type="mean"):
        if type == "mean":
            return np.mean(embeddings, axis=0)
        elif type == "max":
            return np.max(embeddings, axis=0)
        elif type == "min":
            return np.min(embeddings, axis=0)
        elif type == 'weighted':
            raise NotImplementedError("Weighted merge not implemented yet")
        else:
            raise ValueError(f"Invalid merge type: {type}")

    def create_embeddings(self):
        embeddings = self.text['file_id']
        if self.params["recursive"]:
            chunker = RecursiveCharacterTextSplitter(chunk_size=self.params.get("chunk_size", 1000), chunk_overlap=self.params.get("chunk_overlap", 200))
            embeddings['page_embedding'] = self.text['text_sep'].apply(lambda x: self.merge_embeddings([self.model.encode(chunk, convert_to_tensor=True) for chunk in chunker.create_documents([" ".join(page) for page in x])], type=self.params["merge_type"]))
            embeddings['file_embedding'] = self.text['page_embedding'].apply(lambda x: self.merge_embeddings(x, type=self.params["merge_type"]))
        else:
            embeddings['page_embedding'] = self.text['text_sep'].apply(lambda x: self.page_embedding(x))
            embeddings['file_embedding'] = self.text['text_sep'].apply(lambda x: self.file_embedding(x))
        self.embeddings = embeddings
    
    def load_df(self, path):
        if path.endswith(".csv"):
            return pd.read_csv(path)
        elif path.endswith(".pkl"):
            return pd.read_pickle(path)
        else:
            raise ValueError(f"Invalid file type: {path}")


    def save_df(self, path, type='csv'):
        if not os.path.exists(path):
            os.makedirs(path)

        if type == 'csv':
            self.embeddings.to_csv(os.path.join(path, "embeddings.csv"), index=False)
            self.text.to_csv(os.path.join(path, "text.csv"), index=False)
        elif type == 'pkl':
            self.embeddings.to_pickle(os.path.join(path, "embeddings.pkl"))
            self.text.to_pickle(os.path.join(path, "text.pkl"))
        else:
            raise ValueError(f"Invalid save type: {type}")

if __name__ == "__main__":
    params = {
        "model_name": "clips/e5-small-trm-nl",
        "path_to_text": "../../../../data/test_data.csv",
        "recursive": True,
        "merge_type": "mean",
        "chunking": True,
        "chunk_size": 1000,
        "chunk_overlap": 200
    }

    embedder = SemanticEmbedder(params)
    embedder.create_embeddings()