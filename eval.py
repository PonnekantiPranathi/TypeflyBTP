import tiktoken
import time
from controller.llm_controller import LLMController
from controller.minispec_interpreter import MiniSpecInterpreter
from controller.utils import print_t
from controller.llm_wrapper import LLMWrapper

# 1 & Find an apple and go to it. & & & & &  \\
# 2 & Go to the person behind you. & & & & & \\
# 3 & Take a picture of the chair. & & & & &  \\
# 4 & Find something edible. & & & & &  \\
# 5 & Find something red and sweet. & & & & &  \\
# 6 & Can you take pictures of each of the edible objects on the table? & & & & &  \\
# 7 & How many kinds of fruit you can see? & & & & &  \\
# 8 & Go to the largest item you can see. & & & & &  \\
# 9 & Go to the object that is closest to the chair. & & & & &  \\
# 10 & Could you find an apple? If so, go to it. & & & & &  \\
# 11 & If you can see more than 2 people, turn to the left person. &  & & & & \\
# 12 & Can you find something for me to eat? If you can, go for it and return, otherwise find and go to something drinkable. & & &  & & \\
# 13 & Turn around until you see a person with a cup in hand. &  & & & &\\

task_list = [
    {
        "id": 1,
        "task": "Go to the person behind you",
        "scene": "[]",
        "minispec_plan": "tc,180;_1=s,person;?_1==True{o,person;a}",
        "python_plan": """
drone.tc(180)
var_1 = high_level_skillset.sweeping("person")
if var_1 == True:
    high_level_skillset.orienting("person")
    high_level_skillset.approach()
"""
    },
    {
        "id": 2,
        "task": "Take a picture of the chair.",
        "scene": "[char_1 x:0.58 y:0.5 width:0.43 height:0.7 color:gray]",
        "minispec_plan": "o,char_1;p",
        "python_plan": """
high_level_skillset.orienting("char_1")
high_level_skillset.picture()
"""
    },
    {
        "id": 3,
        "task": "[Q] How many kinds of fruit you can see?",
        "scene": "[apple_1 x:0.7 y:0.4 width:0.1 height:0.1 color:red, orange_1 x:0.5 y:0.5 width:0.1 height:0.1 color:orange, banana_1 x:0.3 y:0.6 width:0.1 height:0.1 color:yellow]",
        "minispec_plan": "l,'I can see 3 kinds of fruit.'",
        "python_plan": """
high_level_skillset.log("I can see 3 kinds of fruit.")
"""
    },
    {
        "id": 4,
        "task": "Go to the largest item you can see",
        "scene": "[apple_1 x:0.7 y:0.4 width:0.1 height:0.1 color:red, keyboard_2 x:0.21 y:0.24 width:0.37 height:0.45 color:black, person_3 x:0.58 y:0.5 width:0.43 height:0.7 color:gray]",
        "minispec_plan": "o,person_3;a",
        "python_plan": """
high_level_skillset.orienting("person_3")
high_level_skillset.approach()
"""
    },
    {
        "id": 5,
        "task": "Find something yellow and sweet",
        "scene": "[]",
        "minispec_plan": "8{_1=q,'what's the yellow and sweet target?';?_1!=False{o,_1;a;->True}tc,45}->False",
        "python_plan": """
for i in range(8):
    var_1 = high_level_skillset.query("what's the yellow and sweet target?")
    if var_1 != False:
        high_level_skillset.orienting(var_1)
        high_level_skillset.approach()
        return True
    drone.tc(45)
"""
    },
    {
        "id": 6,
        "task": "Can you find something for cutting paper on the table? The table is on your left.",
        "scene": "[]",
        "minispec_plan": "tc,90;8{_1=q,'what's the object for cutting paper on the table?';?_1!=False{o,_1;a;->True}tc,45}->False",
        "python_plan": """
drone.tc(90)
for i in range(8):
    var_1 = high_level_skillset.query("what's the object for cutting paper on the table?")
    if var_1 != False:
        high_level_skillset.orienting(var_1)
        high_level_skillset.approach()
        return True
    drone.tc(45)
"""
    },
    {
        "id": 7,
        "task": "Go to the object that is closest to the chair",
        "scene": "[apple_1 x:0.7 y:0.4 width:0.1 height:0.1 color:red, orange_1 x:0.5 y:0.5 width:0.1 height:0.1 color:orange, banana_1 x:0.3 y:0.6 width:0.1 height:0.1 color:yellow]",
        "minispec_plan": "8{_1=q,'what is the object closest to the chair?';?_1!=False{o,_1;a;->True}tc,45}->False",
        "python_plan": """
for i in range(8):
    var_1 = high_level_skillset.query("what is the object closest to the chair?")
    if var_1 != False:
        high_level_skillset.orienting(var_1)
        high_level_skillset.approach()
        return True
    drone.tc(45)
"""
    },
    {
        "id": 8,
        "task": "Could you find an apple? If so, go to it",
        "scene": "",
        "minispec_plan": "_1=s,apple;?_1==True{o,apple;a}",
        "python_plan": """
var_1 = high_level_skillset.sweeping("apple")
if var_1 == True:
    high_level_skillset.orienting("apple")
    high_level_skillset.approach()
"""
    },
    {
        "id": 9,
        "task": "If you can see more than two people, then turn to the first person you see",
        "scene": "[apple_1 x:0.7 y:0.4 width:0.1 height:0.1 color:red, chair_3 x:0.21 y:0.44 width:0.37 height:0.45 color:black, person_3 x:0.22 y:0.5 width:0.43 height:0.7 color:gray]",
        "minispec_plan": "_1=q,'how many people are there?';?_1>2{o,person_3}",
        "python_plan": """
var_1 = high_level_skillset.query("how many people are there?")
if var_1 > 2:
    high_level_skillset.orienting("person_3")
    high_level_skillset.approach()
"""
    },
    {
        "id": 10,
        "task": "Can you find something for me to eat? If you can, go for it and return, otherwise find and go to something drinkable",
        "scene": "[]",
        "minispec_plan": "8{_1=q,'what's the edible target?';?_1!=False{o,_1;a;->True}tc,45}->False;8{_2=q,'what's the drinkable target?';?_2!=False{o,_2;a;->True}tc,45}->False",
        "python_plan": """
for i in range(8):
    var_1 = high_level_skillset.query("what's the edible target?")
    if var_1 != False:
        high_level_skillset.orienting(var_1)
        high_level_skillset.approach()
        return True
    drone.tc(45)
for i in range(8):
    var_2 = high_level_skillset.query("what's the drinkable target?")
    if var_2 != False:
        high_level_skillset.orienting(var_2)
        high_level_skillset.approach()
        return True
    drone.tc(45)
return False
"""
    },
    {
        "id": 11,
        "task": "Turn around until you see a person with a cup in hand",
        "scene": "[]",
        "minispec_plan": "8{_1=q,'what's the person with a cup in hand?';?_1!=False{o,_1;a;->True}tc,45}->False",
        "python_plan": """
for i in range(8):
    var_1 = high_level_skillset.query("which of person with a cup in hand?")
    if var_1 != False:
        high_level_skillset.orienting(var_1)
        high_level_skillset.approach()
        return True
    drone.tc(45)
return False
"""
    }
]

def generate_plan():
    enc = tiktoken.encoding_for_model("gpt-4")
    controller = LLMController()
    msi = MiniSpecInterpreter()

    # create a txt file to store the result
    result_log = open("result.txt", "w")
    result_list = []
    count = 3

    for task in task_list:
        if task['id'] != 6:
            continue
        print_t(f"Task: {task['task']}")
        print_t(f"Scene: {task['scene']}")
        ave_planning_time = 0
        ave_execution_time = 0
        ave_token_count = 0
        ave_retries = 0
        result_plan = []
        for i in range(count):
            error_history = []
            retries = 1
            t1 = time.time()
            while True:
                plan = controller.planner.request_planning(task['task'], task['scene'], error_message=error_history)
                print_t(f"Plan: {plan}")
                # check syntax
                check = msi.check_syntax(plan)
                if len(check) > 0:
                    print_t(f"Syntax check failed: {check}")
                    error_history.append({ "plan": plan, "error": check })
                    retries += 1
                else:
                    break
            t2 = time.time()
            ave_planning_time += t2 - t1
            t1 = time.time()
            # controller.execute_minispec(plan)
            t2 = time.time()
            ave_execution_time += t2 - t1
            
            token_count = len(enc.encode(plan))
            ave_token_count += token_count
            ave_retries += retries
        
        ave_planning_time /= count
        ave_execution_time /= count
        ave_token_count /= count
        ave_retries /= count
        print_t(f"Average planning time: {ave_planning_time}, average execution time: {ave_execution_time}, average token count: {ave_token_count}, average retries: {ave_retries}")
        result_list.append({
            "id": task['id'],
            "plan": plan,
            "ave_planning_time": ave_planning_time,
            "ave_execution_time": ave_execution_time,
            "ave_token_count": ave_token_count,
            "ave_retries": ave_retries
        })

    result_log.write(str(result_list))

def comparison():
    enc = tiktoken.encoding_for_model("gpt-4")
    llm = LLMWrapper()
    preamble = "Please generate the exact following code: "
    result = []
    for task in task_list:
        id = task['id']
        plan_minispec = task['minispec_plan']
        plan_python = task['python_plan']
        token_count_minispec = len(enc.encode(plan_minispec))
        token_count_python = len(enc.encode(plan_python))

        t1 = time.time()
        response_minispec = llm.request(preamble + plan_minispec)
        t2 = time.time()
        t_minispec = t2 - t1
        t1 = time.time()
        response_python = llm.request(preamble + plan_python)
        t2 = time.time()
        t_python = t2 - t1
        print_t(f"Task: {task['task']} ({id}) Minispec: {response_minispec} Python: {response_python}")
        print_t(f"id: {id} Token count: {token_count_minispec} {t_minispec} vs {token_count_python} {t_python}")
        result.append(f"{id} & {token_count_minispec} & {t_minispec:.2f} & {token_count_python} & {t_python:.2f} \\\\")

    print("\n".join(result))

if __name__ == "__main__":
    generate_plan()
    # comparison()
