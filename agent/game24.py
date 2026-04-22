from game24_prompt import propose_prompt, value_prompt
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def chatgpt(prompt, model = 'gpt-4', n = 1) -> list:
    messages = [{ 'role':'user', 'content': prompt}]
    outputs = []
    while n > 0:
        cnt = min(n, 20)
        n -= cnt
        res = client.chat.completions.create(
            model = model,
            messages = messages,
            n = cnt
        )
        print('Result:', res)
        outputs.extend([choice.message.content for choice in res.choices])
        print('Outputs:', outputs)
    return outputs

def first_think(input):
    proposals = chatgpt(propose_prompt.format(input=input))[0].split('\n')
    print(proposals)

    proposals = [_ + '\n' for _ in proposals]
    print('Proposals:', proposals)

    # Create index list
    ids = list(range(len(proposals)))
    print('ids:', ids)

    return (ids, proposals)

def first_evaluate(proposals):
    pass

def first_screen(ids, values):
    pass

def second_think(input):
    pass

def second_evaluate(proposals):
    pass

def second_screen(ids, values):
    pass

def third_think(input):
    pass

def third_evaluate(proposals):
    pass

def third_screen(ids, values):
    pass

def GetResult(result):
    print(f'Input number:{input}')
    if(len(result) == 0):
        print('Cannot get result for game 24.')
    else:
        print('Game 24 calc expressions:')
        for r in result:
            print('==========')
            print(r)

if __name__ == '__main__':
    value_cache = []
    input = '5 8 11 13'

    print('Round 1: thinking...')
    ids, proposals = first_think(input)
    print('Round 1: think result:', ids, proposals)

    print('Round 1: evaluating...')
    values = first_evaluate(input)
    print('Round 1: evaluate result:', values)

    print('Round 1: filtering...')
    select_proposals = first_screen(ids, proposals)
    print('Round 1: filter result:', select_proposals)

    print('Round 2: thinking...')
    ids, proposals = second_think(select_proposals)
    print('Round 2: think result:', ids, proposals)

    print('Round 2: evaluating...')
    values = second_evaluate(input)
    print('Round 2: evaluate result:', values)

    print('Round 2: filtering...')
    select_proposals = second_screen(values)
    print('Round 2: filter result:', select_proposals)

    print('Round 3: thinking...')
    ids, proposals = third_think(select_proposals)
    print('Round 3: think result:', ids, proposals)

    print('Round 3: evaluating...')
    values = third_evaluate(input)
    print('Round 3: evaluate result:', values)

    print('Round 3: filtering...')
    select_proposals = third_screen(values)
    print('Round 3: filter result:', select_proposals)