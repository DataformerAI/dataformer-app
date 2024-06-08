from dfapp.base.models.model import LCModelComponent
from dfapp.field_typing import BaseLanguageModel
from datasets import DatasetDict, Dataset
from tqdm import tqdm
import random


class EvolInstructGeneratorComponent(LCModelComponent):
    display_name = "Evol Instruct Generator"
    description = "Generate responses using Evol Instruct model and output a new DatasetDict."

    def createBreadthPrompt(self, instruction, base_instruction_creater):
        prompt = base_instruction_creater + "\n#Given Prompt#\n" + instruction + "\n#Created Prompt#\n"
        return prompt

    def createConstraintsPrompt(self, instruction, base_instruction_writer):
        prompt = base_instruction_writer.format("Please add one more constraints/requirements into #The Given Prompt#")
        prompt += "\n#The Given Prompt#\n" + instruction + "\n#Rewritten Prompt#\n"
        return prompt

    def createDeepenPrompt(self, instruction, base_instruction_writer):
        prompt = base_instruction_writer.format(
            "If #The Given Prompt# contains inquiries about certain issues, the depth and breadth of the inquiry can be increased."
        )
        prompt += "\n#The Given Prompt#\n" + instruction + "\n#Rewritten Prompt#\n"
        return prompt

    def createConcretizingPrompt(self, instruction, base_instruction_writer):
        prompt = base_instruction_writer.format("Please replace general concepts with more specific concepts.")
        prompt += "\n#The Given Prompt#\n" + instruction + "\n#Rewritten Prompt#\n"
        return prompt

    def createReasoningPrompt(self, instruction, base_instruction_writer):
        prompt = base_instruction_writer.format(
            "If #The Given Prompt# can be solved with just a few simple thinking processes, you can rewrite it to explicitly request multiple-step reasoning."
        )
        prompt += "\n#The Given Prompt#\n" + instruction + "\n#Rewritten Prompt#\n"
        return prompt

    def build_config(self):
        return {
            "Column_name": {"display_name": "Column", "required": True},
            "Breadth_Prompt": {"display_name": "Breadth Prompt", "multiline": True, "advanced": True},
            "Constraints_Prompt": {"display_name": "Constraints Prompt", "multiline": True, "advanced": True},
            "Deepen_Prompt": {"display_name": "Deepen Prompt", "multiline": True, "advanced": True},
            "Concretizing_Prompt": {"display_name": "Concretizing Prompt", "multiline": True, "advanced": True},
            "Reasoning_Prompt": {"display_name": "Reasoning Prompt", "multiline": True, "advanced": True},
        }

    def build(
        self,
        Column_name: str,
        dataset: DatasetDict,
        model: BaseLanguageModel,
        Breadth_Prompt: str = "I want you act as a Prompt Creator.\r\n\
            Your goal is to draw inspiration from the #Given Prompt# to create a brand new prompt.\r\n\
            This new prompt should belong to the same domain as the #Given Prompt# but be even more rare.\r\n\
            The LENGTH and complexity of the #Created Prompt# should be similar to that of the #Given Prompt#.\r\n\
            The #Created Prompt# must be reasonable and must be understood and responded by humans.\r\n\
            '#Given Prompt#', '#Created Prompt#', 'given prompt' and 'created prompt' are not allowed to appear in #Created Prompt#\r\n",
        Constraints_Prompt: str = "I want you act as a Prompt Rewriter.\r\n \
            Your objective is to rewrite a given prompt into a more complex version to make those famous AI systems (e.g., chatgpt and GPT4) a bit harder to handle.\r\n \
            But the rewritten prompt must be reasonable and must be understood and responded by humans.\r\n \
            Your rewriting cannot omit the non-text parts such as the table and code in #The Given Prompt#:. Also, please do not omit the input in #The Given Prompt#. \r\n \
            You SHOULD complicate the given prompt using the following method: \r\n\
            Add one more constraint/requirement into #The Given Prompt#.\r\n\
            You should try your best not to make the #Rewritten Prompt# become verbose, #Rewritten Prompt# can only add 10 to 20 words into #The Given Prompt#. \r\n\
            '#The Given Prompt#', '#Rewritten Prompt#', 'given prompt' and 'rewritten prompt' are not allowed to appear in #Rewritten Prompt#\r\n",
        Deepen_Prompt: str = "I want you act as a Prompt Rewriter.\r\n \
            Your objective is to rewrite a given prompt into a more complex version to make those famous AI systems (e.g., chatgpt and GPT4) a bit harder to handle.\r\n \
            But the rewritten prompt must be reasonable and must be understood and responded by humans.\r\n \
            Your rewriting cannot omit the non-text parts such as the table and code in #The Given Prompt#:. Also, please do not omit the input in #The Given Prompt#. \r\n \
            You SHOULD complicate the given prompt using the following method: \r\n\
            Increase the depth and breadth of the inquiry in #The Given Prompt#.\r\n\
            You should try your best not to make the #Rewritten Prompt# become verbose, #Rewritten Prompt# can only add 10 to 20 words into #The Given Prompt#. \r\n\
            '#The Given Prompt#', '#Rewritten Prompt#', 'given prompt' and 'rewritten prompt' are not allowed to appear in #Rewritten Prompt#\r\n",
        Concretizing_Prompt: str = "I want you act as a Prompt Rewriter.\r\n \
            Your objective is to rewrite a given prompt into a more complex version to make those famous AI systems (e.g., chatgpt and GPT4) a bit harder to handle.\r\n \
            But the rewritten prompt must be reasonable and must be understood and responded by humans.\r\n \
            Your rewriting cannot omit the non-text parts such as the table and code in #The Given Prompt#:. Also, please do not omit the input in #The Given Prompt#. \r\n \
            You SHOULD complicate the given prompt using the following method: \r\n\
            Replace general concepts with more specific ones in #The Given Prompt#.\r\n\
            You should try your best not to make the #Rewritten Prompt# become verbose, #Rewritten Prompt# can only add 10 to 20 words into #The Given Prompt#. \r\n\
            '#The Given Prompt#', '#Rewritten Prompt#', 'given prompt' and 'rewritten prompt' are not allowed to appear in #Rewritten Prompt#\r\n",
        Reasoning_Prompt: str = "I want you act as a Prompt Rewriter.\r\n \
            Your objective is to rewrite a given prompt into a more complex version to make those famous AI systems (e.g., chatgpt and GPT4) a bit harder to handle.\r\n \
            But the rewritten prompt must be reasonable and must be understood and responded by humans.\r\n \
            Your rewriting cannot omit the non-text parts such as the table and code in #The Given Prompt#:. Also, please do not omit the input in #The Given Prompt#. \r\n \
            You SHOULD complicate the given prompt using the following method: \r\n\
            Explicitly request multiple-step reasoning if #The Given Prompt# can be solved with just a few simple thinking processes.\r\n\
            You should try your best not to make the #Rewritten Prompt# become verbose, #Rewritten Prompt# can only add 10 to 20 words into #The Given Prompt#. \r\n\
            '#The Given Prompt#', '#Rewritten Prompt#', 'given prompt' and 'rewritten prompt' are not allowed to appear in #Rewritten Prompt#\r\n",
    ) -> DatasetDict:
        df = dataset["train"].to_pandas().head(2)
        question_responses = []
        answer_response = []

        for instruction in tqdm(df[Column_name], desc="Generating prompts"):
            evol_prompts = [
                self.createBreadthPrompt(instruction, Breadth_Prompt),
                self.createConstraintsPrompt(instruction, Constraints_Prompt),
                self.createDeepenPrompt(instruction, Deepen_Prompt),
                self.createConcretizingPrompt(instruction, Concretizing_Prompt),
                self.createReasoningPrompt(instruction, Reasoning_Prompt),
            ]
            selected_evol_prompt = random.choice(evol_prompts)
            chat_completion = self.get_chat_result(model, False, selected_evol_prompt)
            answer = self.get_chat_result(model, False, chat_completion)
            question_responses.append(chat_completion)
            answer_response.append(answer)
        df["instruction"] = question_responses
        df["output"] = answer_response
        new_dataset = Dataset.from_pandas(df)
        new_dataset = DatasetDict({"train": new_dataset})
        return new_dataset
