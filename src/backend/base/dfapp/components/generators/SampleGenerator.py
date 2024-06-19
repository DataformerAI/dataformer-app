from dfapp.base.models.model import LCModelComponent
from dfapp.field_typing import BaseLanguageModel
from datasets import DatasetDict, Dataset
from tqdm import tqdm
import random
import pandas as pd
import asyncio

class SampleGeneratorComponent(LCModelComponent):
    display_name = "Sample Generator"
    description = "Generate a specified number of samples based on user input"

    def build_config(self):
        return {
            "System Prompt": {"display_name": "System Prompt", "multiline": True},
            "Question Column": {"display_name": "Question Column Name"},
            "Target Sample Count": {"display_name": "Target Sample Count"},
            "max_requests": {
                "display_name": "Max Requests per Minute",
                "advanced": True,
            },
            "max_attempts": {
                "display_name": "Max Attempts",
                "info": "Max retry attempts to make if api call fails",
                "advanced": True,
            }
        }

    def build(
        self,
        dataset: DatasetDict,
        model: BaseLanguageModel,
        question_column: str = "Sample",
        target_sample_count: int = 100,
        system_prompt: str = "",
        max_requests: int = 20,
        max_attempts: int = 3,
    ) -> DatasetDict:
        df = dataset["train"].to_pandas()
        seed_samples = list(df[question_column])
        data_instructions = []
        system_prompt = f"{system_prompt}\n\nYou are an advanced AI assistant. Extract keywords from the provided context and generate a new sample using them. Output only the sample, no additional instructions or explanations."

        while len(data_instructions) < target_sample_count:
            seed_sample = random.choice(seed_samples)
            prompt = f"Generate a new sample that mirrors the content and style of the following input:\n\n{seed_sample}"
            data_instructions.append(prompt)

        loop = asyncio.get_event_loop()
        answers = loop.run_until_complete(self.datagen_bulk(model, data_instructions, system_prompt, max_requests, max_attempts))
        seed_samples.extend(answers)

        new_df = pd.DataFrame(seed_samples, columns=[question_column])
        new_dataset = Dataset.from_pandas(new_df)
        new_dataset_dict = DatasetDict({"train": new_dataset})
        return new_dataset_dict
