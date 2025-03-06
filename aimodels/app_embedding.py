""" 
Description: 
 - AiReport project. This is a demo POC project, it is not intented
   for production. The quality of the code is not guaranteed. 
   
   If you refrence the code in this project, it means that you understand
   the risk and you are responsible for any issues caused by the code.

History:
 - 2025/01/20 by Hysun (hysun.he@oracle.com): Initial implementation.
"""

from dao import selectai_util
from langchain_core.embeddings import Embeddings
from typing import List


class CustomSelectAiEmbeddings(Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return selectai_util.embedding_invoke(docs=texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


embedding_model = CustomSelectAiEmbeddings()
