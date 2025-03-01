""" 
Description: 
 - AiReport project.

History:
 - 2024/07/23 by Hysun (hysun.he@oracle.com): Created
"""

from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from conf import app_config
from aimodels import oci_genai


class OciGenAILLM(ChatOCIGenAI):
    def invoke(self, prompt: str) -> str:
        if "llama" in app_config.OCI_GENAI_MODEL:
            return oci_genai.llm_invoke_llama(prompt)
        elif "cohere" in app_config.OCI_GENAI_MODEL:
            return oci_genai.llm_invoke_cohere(prompt)
        else:
            raise NotImplementedError("!!! Invalid LLM specified!")


llm_model = OciGenAILLM(
    model_id=app_config.OCI_GENAI_MODEL,
    service_endpoint=app_config.OCI_SERVICE_ENDPOINT,
    compartment_id=app_config.OCI_GENAI_COMPARTMENT,
    model_kwargs={"temperature": 0, "max_tokens": 4000},
)
