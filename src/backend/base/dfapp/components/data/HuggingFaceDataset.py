from dfapp.custom import CustomComponent
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
        dataset = load_dataset(dataset_name, use_auth_token=huggingface_token if huggingface_token else None)
        dataset['train'].to_json(f"/home/utkarshraj/Desktop/dataformer-app-fork11/src/frontend/public/{dataset_name}_train.jsonl")
        return dataset
