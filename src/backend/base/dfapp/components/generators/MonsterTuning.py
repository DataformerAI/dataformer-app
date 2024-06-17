from dfapp.base.models.model import LCModelComponent
from dfapp.base.models.finetuningmodel import MODEL_NAMES
from monsterapi import client as mclient
from dfapp.field_typing import Text

class MonsterGeneratorComponent(LCModelComponent):
    display_name = "MonsterFinetuning Generator"
    description = "Finetune your desired dataset with a few clicks"

    def build_config(self):
        return {
            "model_name": {
                "display_name": "Model",
                "info": "The name of the model to use. Supported examples: mistralai/Mistral-7B-v0.1",
                "options": MODEL_NAMES,
            },
            "Monster_api_key": {
                "display_name": "Monster API Key",
                "info": "API key for the Monster API for finetuning.",
                "password": True,
                "required": True
            },
            "dataset_name": {
                "display_name": "Dataset Name",
                "info": "Name of the dataset for finetuning.",
                "required": True
            },
            "Input": {
                "display_name": "Input Column",
                "info": "Input Column of Dataset.",
                "required": True
            },
            "Output": {
                "display_name": "Output Column",
                "info": "Output Column of Dataset.",
                "required": True
            }
        }

    def build(
        self,
        Monster_api_key: str,
        model_name: str,
        dataset_name: str,
        Input: str,
        Output: str,
    ) -> Text:
        launch_payload = {
            "pretrainedmodel_config": {
                "model_path": model_name,
                "use_lora": True,
                "lora_r": 8,
                "lora_alpha": 16,
                "lora_dropout": 0,
                "lora_bias": "none",
                "use_quantization": False,
                "use_gradient_checkpointing": False,
                "parallelization": "nmp"
            },
            "data_config": {
                "data_path": dataset_name,
                "data_subset": "default",
                "data_source_type": "hub_link",
                "prompt_template": f"Here is an example on how to use {dataset_name} dataset ### Input: {Input} ### Output: {Output}",
                "cutoff_len": 512,
                "prevalidated": False
            },
            "training_config": {
                "early_stopping_patience": 5,
                "num_train_epochs": 1,
                "gradient_accumulation_steps": 1,
                "warmup_steps": 50,
                "learning_rate": 0.001,
                "lr_scheduler_type": "reduce_lr_on_plateau",
                "group_by_length": False
            },
            "logging_config": { "use_wandb": False }
            }
        from monsterapi import client as mclient
        client = mclient(api_key=Monster_api_key)
        ret = client.finetune(service="llm", params=launch_payload)
        ret = "Finetuning is been Starting on Following creditals" + " " + str(ret)
        return str(ret)
