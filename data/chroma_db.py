from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from .sqlite_db import NarouDB
import os
import json

#### INDEXING ####

class NarouReviewsDB():
    def __init__(self, db_path="chroma"):
        self.vectorstore = Chroma(persist_directory=db_path,
                                  embedding_function=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
                                  collection_name="narou_reviews"
                                )
    
    def get_retriever(self, search_kwargs={"k": 4}):
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)

    def _load_reviews(self,root = "raw/reviews", encoding="utf-8"):
        db = NarouDB()
        db.connect()
        root = os.path.abspath(root)
        docs = []
        for dirname in os.listdir(os.path.join(root)):
            novel_name = db.get_novel_name(dirname)
            for filename in os.listdir(os.path.join(root, dirname)):
                path = os.path.join(root, dirname, filename)
                for i,review in enumerate(json.load(open(path, encoding=encoding))):
                    doc = Document(page_content=review["body"],
                            metadata={
                                "title":review["title"],
                                "date":review["date"],
                                "ncode": dirname,
                                "novel_name": novel_name,
                                "doc_id": f"{dirname}/{filename}",
                                "review_id": i,
                            })
                    docs.append(doc)
        return docs
    
    def upsert_reviews(self, path="raw/reviews"):
        # Load Documents
        docs = self._load_reviews(path)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
        splits = text_splitter.split_documents(docs)
        split_ids = []
        for split in splits:
            split.metadata["split_id"] = f"{split.metadata['doc_id']}_{split.metadata['review_id']}_{split.metadata['start_index']}"
            split_ids.append(split.metadata["split_id"])
        self.vectorstore.add_documents(splits, ids=split_ids)
        

# retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
# # Load Documents
# #TODO: Replace with your own loader
# docs = load_reviews1("raw/reviews")
# # Split
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# splits = text_splitter.split_documents(docs)
# docs