from dfapp.interface.custom.custom_component import CustomComponent
from datasets import load_dataset, DatasetDict
from typing import Optional


class HuggingFaceDatasetComponent(CustomComponent):
    display_name = "HuggingFace Dataset"
    description = "Retrieve datasets from Hugging Face."

    def build_config(self):
        return {
            "dataset_name": {"display_name": "Dataset Name", "info": "Name of the dataset to retrieve."},
            "huggingface_token": {
                "display_name": "Hugging Face Token",
                "password": True,
                "info": "Token for Hugging Face API authentication (optional).",
                "required": False,
            },
        }

    def build(self, dataset_name: str, huggingface_token: Optional[str] = None) -> DatasetDict:
        return load_dataset(dataset_name, use_auth_token=huggingface_token if huggingface_token else None)
