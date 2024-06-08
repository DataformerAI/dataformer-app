from dfapp.interface.custom.custom_component import CustomComponent
from dfapp.field_typing import Text
from datasets import DatasetDict, Dataset

class JsonToDatasetComponent(CustomComponent):
    display_name = "Json to Dataset"
    description = "Convert Json data to Huggingface DatasetDict type"
    icon = "merge"

    def build_config(self):
        return {
            "json_data": {
                "display_name": "Json Data",
                "info": "The Json data",
                "required": True,
            }
        }

    def build(self, json_data: list) -> DatasetDict:
        data_list = [item for item in json_data]
        data_dict = {key: [item[key] for item in data_list] for key in data_list[0].keys()}
        dataset = Dataset.from_dict(data_dict)
        dataset_dict = DatasetDict({"train": dataset})
        return dataset_dict
