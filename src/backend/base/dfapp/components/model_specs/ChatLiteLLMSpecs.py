from typing import Any, Dict, Optional

from langchain_community.chat_models.litellm import ChatLiteLLM, ChatLiteLLMException

from dfapp.custom import CustomComponent
from dfapp.field_typing import BaseLanguageModel


class ChatLiteLLMComponent(CustomComponent):
    display_name = "ChatLiteLLM"
    description = "`LiteLLM` collection of large language models."
    documentation = "https://python.langchain.com/docs/integrations/chat/litellm"

    def build_config(self):
        return {
            "model": {
                "display_name": "Model name",
                "field_type": "str",
                "advanced": False,
                "required": True,
                "info": "The name of the model to use. For example, `gpt-3.5-turbo`.",
            },
            "api_key": {
                "display_name": "API key",
                "field_type": "str",
                "advanced": False,
                "required": False,
                "password": True,
            },
            "provider": {
                "display_name": "Provider",
                "info": "The provider of the API key.",
                "options": [
                    "OpenAI",
                    "Azure",
                    "Anthropic",
                    "Replicate",
                    "Cohere",
                    "OpenRouter",
                ],
            },
            "streaming": {
                "display_name": "Streaming",
                "field_type": "bool",
                "advanced": True,
                "required": False,
                "default": True,
            },
            "temperature": {
                "display_name": "Temperature",
                "field_type": "float",
                "advanced": False,
                "required": False,
                "default": 0.7,
            },
            "model_kwargs": {
                "display_name": "Model kwargs",
                "field_type": "dict",
                "advanced": True,
                "required": False,
                "default": {},
            },
            "top_p": {
                "display_name": "Top p",
                "field_type": "float",
                "advanced": True,
                "required": False,
            },
            "top_k": {
                "display_name": "Top k",
                "field_type": "int",
                "advanced": True,
                "required": False,
            },
            "n": {
                "display_name": "N",
                "field_type": "int",
                "advanced": True,
                "required": False,
                "info": "Number of chat completions to generate for each prompt. "
                "Note that the API may not return the full n completions if duplicates are generated.",
                "default": 1,
            },
            "max_tokens": {
                "display_name": "Max Tokens",
                "advanced": True,
                "info": "The maximum number of tokens to generate. Set to 0 for unlimited tokens.",
            },
            "max_retries": {
                "display_name": "Max retries",
                "field_type": "int",
                "advanced": True,
                "required": False,
                "default": 6,
            },
            "verbose": {
                "display_name": "Verbose",
                "field_type": "bool",
                "advanced": True,
                "required": False,
                "default": False,
            },
        }

    def build(
        self,
        model: str,
        provider: str,
        api_key: Optional[str] = None,
        streaming: bool = True,
        temperature: Optional[float] = 0.7,
        model_kwargs: Optional[Dict[str, Any]] = {},
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        n: int = 1,
        max_tokens: int = 256,
        max_retries: int = 6,
        verbose: bool = False,
    ) -> BaseLanguageModel:
        try:
            import litellm  # type: ignore

            litellm.drop_params = True
            litellm.set_verbose = verbose
        except ImportError:
            raise ChatLiteLLMException(
                "Could not import litellm python package. " "Please install it with `pip install litellm`"
            )
        provider_map = {
            "OpenAI": "openai_api_key",
            "Azure": "azure_api_key",
            "Anthropic": "anthropic_api_key",
            "Replicate": "replicate_api_key",
            "Cohere": "cohere_api_key",
            "OpenRouter": "openrouter_api_key",
        }
        # Set the API key based on the provider
        api_keys: dict[str, Optional[str]] = {v: None for v in provider_map.values()}

        if variable_name := provider_map.get(provider):
            api_keys[variable_name] = api_key
        else:
            raise ChatLiteLLMException(
                f"Provider {provider} is not supported. Supported providers are: {', '.join(provider_map.keys())}"
            )

        LLM = ChatLiteLLM(
            model=model,
            client=None,
            streaming=streaming,
            temperature=temperature,
            model_kwargs=model_kwargs if model_kwargs is not None else {},
            top_p=top_p,
            top_k=top_k,
            n=n,
            max_tokens=max_tokens,
            max_retries=max_retries,
            openai_api_key=api_keys["openai_api_key"],
            azure_api_key=api_keys["azure_api_key"],
            anthropic_api_key=api_keys["anthropic_api_key"],
            replicate_api_key=api_keys["replicate_api_key"],
            cohere_api_key=api_keys["cohere_api_key"],
            openrouter_api_key=api_keys["openrouter_api_key"],
        )
        return LLM
