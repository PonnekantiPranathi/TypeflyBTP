import os, json, ast
from typing import Union

from skillset import SkillSet
from llm_wrapper import LLMWrapper
from vision_wrapper import VisionWrapper

class LLMPlanner():
    def __init__(self):
        self.llm = LLMWrapper()

        # read prompt from txt
        with open("./assets/planning_prompt.txt", "r") as f:
            self.planning_prompt = f.read()

        with open("./assets/verification_prompt.txt", "r") as f:
            self.verification_prompt = f.read()

        with open("./assets/execution_prompt.txt", "r") as f:
            self.execution_prompt = f.read()

        with open("./assets/rules.txt", "r") as f:
            self.rules = f.read()

        with open("./assets/minispec_syntax.txt", "r") as f:
            self.minispec_syntax = f.read()

        with open("./assets/plan_examples.json", "r") as f:
            self.plan_examples = f.read()

    def init(self, high_level_skillset: SkillSet, low_level_skillset: SkillSet, vision_skill: VisionWrapper):
        self.high_level_skillset = high_level_skillset
        self.low_level_skillset = low_level_skillset
        self.vision_skill = vision_skill

    def request_planning(self, task_description: str):
        # by default, the task_description is an action
        if not task_description.startswith("["):
            task_description = "[A] " + task_description

        prompt = self.planning_prompt.format(system_skill_description_high=self.high_level_skillset,
                                             system_skill_description_low=self.low_level_skillset,
                                             minispec_syntax=self.minispec_syntax,
                                             rules=self.rules,
                                             plan_examples=self.plan_examples,
                                             scene_description=self.vision_skill.get_obj_list(),
                                             task_description=task_description)
        print(f"> Planning request: {task_description}...")
        return ast.literal_eval(self.llm.request(prompt))

    def request_verification(self, prev_task_description: str, prev_task_response: str):
        prompt = self.verification_prompt.format(rules=self.rules,
                                                 scene_description=self.vision_skill.get_obj_list(),
                                                 task_description=prev_task_description,
                                                 response=prev_task_response)
        print(f"> Verification request: {prev_task_description}...")
        return ast.literal_eval(self.llm.request(prompt))
    
    def request_execution(self, question: str) -> Union[bool, str]:
        def parse_value(s):
            # Check for boolean values
            if s.lower() == "true":
                return True
            elif s.lower() == "false":
                return False
            return s
        prompt = self.execution_prompt.format(scene_description=self.vision_skill.get_obj_list(), question=question)
        print(f"> Execution request: {question}...")
        return parse_value(self.llm.request(prompt))