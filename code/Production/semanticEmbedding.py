# semanticEmbedding.py

import torch.nn.functional as F
from torch import Tensor
import torch

from sentence_transformers import SentenceTransformer

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.csv_loader import CSVLoader

import pandas as pd
import numpy as np


'''
SemanticEmbedding class 

    - generates dataframe with critical information + embeddings using sentence transformer 
    - computes similarity between files and between query and files 
    - dataframe structure:
        - file_id
        - file_name
        - text_sep - raw text processed to remove breaks and split into list of lists (list per page containing string)
        - file_embedding
        - page_embedding - dataframe 
        - chunk_embedding - optional, can be used for identifying relevant sections for displaying on frontend
    - embedding structure:
        - file_embedding: embedding of the whole file (all text together)
        - page_embedding: embedding of each page (list of embeddings, one per page)
        - chunk_embedding: embedding of each chunk (list of embeddings, one per chunk)

TODOS


- compare performance for recursive vs full embedding 
    - research has shown that averaging can make better embedding
    - need to check if averaging over chunks in page vs pages in file makes a difference
- fix nested dataframes
    - motivation - have embeddings indexable by page number and chunk number
    - ! index of list currently not working, since some entries are nan (e.g for images)

'''

config = {
    "model_name": "clips/e5-small-trm-nl",
    "path_to_text": "/Users/ingaschoyen/AML_wrapper/AML/data/page_extraction_orig.csv",
    "recursive": False,
    "chunking": False,
    "merge_type": "mean"
}

class SemanticEmbedding:
    def __init__(self, params=config):
        self.params = params
        self.model = SentenceTransformer(params["model_name"])
        print("Model loaded")
        self.df = self.load_files(params["path_to_text"])
        print("Files loaded")


    def load_files(self, path_to_csv):
        df_in = pd.read_csv(path_to_csv)
        df_in['text_sep'] = df_in['raw_text'].str.split("\n")
        print(df_in.head())
        # split text into dictionary with page numbers as keys
        df_out = df_in[['file_id', 'file_name', 'text_sep']].groupby("file_id").apply(
            lambda x: pd.Series({
                'file_name': x['file_name'].iloc[0],
                'text_sep': {i+1: page for i, page in enumerate(x['text_sep'].tolist())}
            })
        ).reset_index()
        print(df_out.head())
            
        return df_out

    def create_embeddings(self):
        if self.params["recursive"]:
            self.embedd_recursively(self.params["merge_type"], chunking=self.params["chunking"])
        else:
            self.embedd_non_recursively(chunking=self.params["chunking"])



    def gen_embeddings(self, text):
        return self.model.encode(text, convert_to_tensor=True)
        
    
    def embedd_non_recursively(self, chunking=False):
        # for each file put all text together per file
        file_text = self.df['text_sep'].apply(lambda x: " ".join(x))
        assert len(file_text) == len(self.df)
        self.df['file_embedding'] = file_text.apply(lambda x: self.gen_embeddings(x))
        # create per page embedding
        self.df['page_embedding'] = self.df['text_sep'].apply(lambda x: [self.gen_embeddings(page) for page in x])
        # if chunking, create chunks and compute embeddings
        if chunking:
            chunker = RecursiveCharacterTextSplitter(chunk_size=self.params.get("chunk_size", 1000), chunk_overlap=self.params.get("chunk_overlap", 200))
            self.df['chunk_embedding'] = self.df['text_sep'].apply(lambda x: [self.gen_embeddings(chunk) for page in x for chunk in chunker.create_documents([page])])



    def embedd_recursively(self, merge_type="mean", chunking=False):
        if chunking:
            chunker = RecursiveCharacterTextSplitter(chunk_size=self.params.get("chunk_size", 1000), chunk_overlap=self.params.get("chunk_overlap", 200))
            self.df['chunk_embedding'] = self.df['text_sep'].apply(lambda x: [self.gen_embeddings(chunk) for page in x for chunk in chunker.create_documents([page])])
            self.df['page_embedding'] = self.df['chunk_embedding'].apply(lambda x: self.merge_embeddings(x, type=merge_type))
        else:
            self.df['page_embedding'] = self.df['text_sep'].apply(lambda x: [self.gen_embeddings(page) for page in x])
        self.df['file_embedding'] = self.df['page_embedding'].apply(lambda x: self.merge_embeddings(x, type=merge_type))



    def merge_embeddings(self, embeddings, type="mean"):
        if type == "mean":
            # stack and take average over the first dimension (number of pages/chunks)
            return torch.mean(torch.stack(embeddings), dim=0)
        elif type == "weighted_mean":
            # implement weighted mean if needed
            pass
        else:        
            raise ValueError("Unsupported merge type")

    def comp_sim_files(self, embeddings):
        return self.model.similarity(embeddings, embeddings)

    def comp_sim_query(self, query_embedding, embeddings):
        return self.model.similarity(query_embedding, embeddings)

    def save_df(self, path):
        self.df.to_csv(path, index=False)


        
def main():
    embedder = SemanticEmbedding(config)
    embedder.create_embeddings()
    embedder.save_df("/Users/ingaschoyen/AML_wrapper/AML/data/embeddings.csv")
    return embedder

if __name__ == "__main__":
    embedder = main()
    print("Done")
    print(embedder.df.head())