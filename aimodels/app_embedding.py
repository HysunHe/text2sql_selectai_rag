""" 
Description: 
 - AiReport project.

History:
 - 2024/07/11 by Hysun (hysun.he@oracle.com): Created
"""

# from langchain.embeddings.huggingface import HuggingFaceEmbeddings
# from conf import app_config
from langchain_core.embeddings import Embeddings
from aimodels import oci_genai
from typing import List


# embedding_model = HuggingFaceEmbeddings(
#     model_name=app_config.EMBEDDING_MODEL,
#     model_kwargs={"device": "cpu"},
# )


class OciEmbeddings(Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return oci_genai.embedding_invoke(docs=texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


embedding_model = OciEmbeddings()
