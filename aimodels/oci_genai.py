""" 
Description: 
 - AiReport project.

History:
 - 2024/07/11 by Hysun (hysun.he@oracle.com): Created
"""

import oci
from conf import app_config
from oci.generative_ai_inference import GenerativeAiInferenceClient
from langchain_core.messages import BaseMessage

from typing import List

generative_ai_inference_client: GenerativeAiInferenceClient = None


def get_oci_ai_client():
    global generative_ai_inference_client

    if generative_ai_inference_client:
        return generative_ai_inference_client

    generative_ai_inference_client = GenerativeAiInferenceClient(
        config=oci.config.from_file(
            app_config.OCI_CONFIG_FILE, app_config.OCI_CONFIG_PROFILE
        ),
        service_endpoint=app_config.OCI_SERVICE_ENDPOINT,
        retry_strategy=oci.retry.ExponentialBackoffWithFullJitterRetryStrategy(
            base_sleep_time_seconds=60,
            exponent_growth_factor=0.1,
            max_wait_between_calls_seconds=180,
            checker_container=oci.retry.retry_checkers.RetryCheckerContainer(
                [oci.retry.retry_checkers.LimitBasedRetryChecker(max_attempts=5)]
            ),
        ),
        timeout=(20, 300),
    )
    return generative_ai_inference_client


def llm_invoke_cohere(prompt: str) -> str:
    """Get texts from LLM model for given prompts using OCI Generative AI Service."""
    generative_ai_inference_client: GenerativeAiInferenceClient = get_oci_ai_client()

    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    chat_request = oci.generative_ai_inference.models.CohereChatRequest()
    chat_request.message = prompt
    chat_request.max_tokens = 4000
    chat_request.temperature = 0.01
    chat_request.frequency_penalty = 0
    chat_request.top_p = 0.8
    chat_request.top_k = 3

    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
        model_id=app_config.OCI_GENAI_MODEL
    )
    chat_detail.chat_request = chat_request
    chat_detail.compartment_id = app_config.OCI_GENAI_COMPARTMENT
    chat_response = generative_ai_inference_client.chat(chat_detail)

    msg: BaseMessage = BaseMessage(
        content=chat_response.data.chat_response.text, type="str"
    )
    return msg


def llm_invoke_llama(prompt: str) -> str:
    """Get texts from LLM model for given prompts using OCI Generative AI Service."""
    generative_ai_inference_client: GenerativeAiInferenceClient = get_oci_ai_client()

    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    content = oci.generative_ai_inference.models.TextContent()
    content.text = prompt
    message = oci.generative_ai_inference.models.Message()
    message.role = "USER"
    message.content = [content]
    chat_request = oci.generative_ai_inference.models.GenericChatRequest()
    chat_request.api_format = (
        oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
    )
    chat_request.messages = [message]
    chat_request.max_tokens = 4000
    chat_request.temperature = 0.01
    chat_request.frequency_penalty = 0
    chat_request.top_p = 0.8
    chat_request.top_k = 3

    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
        model_id=app_config.OCI_GENAI_MODEL
    )
    chat_detail.chat_request = chat_request
    chat_detail.compartment_id = app_config.OCI_GENAI_COMPARTMENT
    response = generative_ai_inference_client.chat(chat_detail)

    msg: BaseMessage = BaseMessage(
        content=response.data.chat_response.choices[0].message.content[0].text,
        type="str",
    )
    return msg


def embedding_invoke(docs: List[str]) -> List[List[float]]:
    generative_ai_inference_client: GenerativeAiInferenceClient = get_oci_ai_client()

    embed_text_detail = oci.generative_ai_inference.models.EmbedTextDetails()
    embed_text_detail.serving_mode = (
        oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=app_config.EMBEDDING_MODEL
        )
    )
    embed_text_detail.inputs = docs
    embed_text_detail.truncate = "NONE"
    embed_text_detail.compartment_id = app_config.OCI_GENAI_COMPARTMENT
    embed_text_response = generative_ai_inference_client.embed_text(embed_text_detail)

    return embed_text_response.data.embeddings
