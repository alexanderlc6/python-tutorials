import time
import uuid

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task
from langgraph.types import interrupt, Command

@task
def write_essay(topic:str) -> str :
    time.sleep(1)
    return f'An essay about topic {topic}'

human_review = True

@entrypoint(checkpointer=InMemorySaver())
def workflow(topic:str) -> dict:
    essay = write_essay('cat').result()
    is_approved = interrupt({'essay': essay, 'action': 'Please approve/reject the essay'})

    return {
        # The essay that was generated
        'essay': essay,
        # Response from HIL
        'is_approved': is_approved
    }

def my_workflow(some_input: dict) -> int:
    # e.g.involve long-running tasks like API calls and may be interrupted for human-in-the-loop
    return 0

thread_id = str(uuid.uuid4())
config = {'configurable': {'thread_id': thread_id}}

for item in workflow.stream(Command(resume=human_review), config):
    print(item)

# {'write_essay': 'An essay about topic cat'}
# {'__interrupt__': (Interrupt(value={'essay': 'An essay about topic cat', 'action': 'Please approve/reject the essay'}, id='8657c40c4bb011d570a3e31720fbb3ec'),)}

# {'write_essay': 'An essay about topic cat'}
# {'workflow': {'essay': 'An essay about topic cat', 'is_approved': True}}