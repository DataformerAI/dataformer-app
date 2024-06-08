from dfapp.field_typing import BaseLanguageModel
from datasets import DatasetDict, Dataset
from tqdm import tqdm
import pandas as pd
from dfapp.custom import CustomComponent

class DatasetMergerComponent(CustomComponent):
    display_name = "Dataset Merger"
    description = "Merge Dataset dict into one Dataset"

    def build(
        self,
        dataset1: DatasetDict,
        dataset2: DatasetDict,
    ) -> DatasetDict:
        merged_dataset = DatasetDict()

        for split in dataset1.keys():
            if split in dataset2:
                df1 = dataset1[split].to_pandas()
                df2 = dataset2[split].to_pandas()

                # Ensure both dataframes have the same columns, filling missing ones with NaN
                all_columns = set(df1.columns).union(set(df2.columns))
                df1 = df1.reindex(columns=all_columns, fill_value=pd.NA)
                df2 = df2.reindex(columns=all_columns, fill_value=pd.NA)

                # Concatenate along rows
                merged_df = pd.concat([df1, df2], axis=0)

                # Reset index to avoid the __index_level_0__ column
                merged_df = merged_df.reset_index(drop=True)
                merged_dataset[split] = Dataset.from_pandas(merged_df)
                
        return merged_dataset
