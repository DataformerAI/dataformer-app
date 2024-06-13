from dfapp.base.models.model import LCModelComponent
from dfapp.field_typing import BaseLanguageModel
from datasets import DatasetDict, Dataset
from tqdm import tqdm
import random
import pandas as pd

class SampleGeneratorComponent(LCModelComponent):
    display_name = "Sample Generator"
    description = "Generate a specified number of samples based on user input"

    def build_config(self):
        return {
            "System Prompt": {"display_name": "System Prompt", "multiline": True},
            "Question Column": {"display_name": "Question Column Name"},
            "Target Sample Count": {"display_name": "Target Sample Count"}
        }

    def build(
        self,
        dataset: DatasetDict,
        model: BaseLanguageModel,
        question_column: str = "Sample",
        target_sample_count: int = 100,
        system_prompt: str = ""
    ) -> DatasetDict:
        df = dataset["train"].to_pandas().head(20)
        seed_samples = list(df[question_column])
        expanded_samples = []
        while len(expanded_samples) < target_sample_count:
            seed_sample = random.choice(seed_samples)
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"You are an advanced AI assistant. Extract keywords from the provided context and generate a sample using them. Output only, no additional instructions needed. {system_prompt}"),
                ("human", f"Generate a new sample similar to: {seed_sample}"),
            ])
            try:
                chain = prompt | model
                new_sample = chain.invoke({"input": seed_sample})
                expanded_samples.append(new_sample.content)
            except Exception as e:
                print(f"Error generating sample: {e}")
                continue

        new_df = pd.DataFrame(expanded_samples, columns=[question_column])
        new_dataset = Dataset.from_pandas(new_df)
        new_dataset_dict = DatasetDict({"train": new_dataset})

        return new_dataset_dict