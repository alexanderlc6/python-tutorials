from sympy.physics.units import temperature
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# =========Phase I: Load model =========
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained('gpt2')
print(type(tokenizer))
print(dir(tokenizer))

inputs = tokenizer("Today the weather is good, I want to go to", return_tensors="pt")

# Method1: Manually generate token(forbidden for gradual calculation)
# with torch.no_grad():
#     # Forward broadcasting
#     # output: logits - predict [batch_size, seq_len, vocab_size][batch_size, seq_len, vocab_size], e.g.[[0.1, -0.5, 2.3, ..., 0.02],[0.3,  1.2, -0.1, ..., -0.5],...]
#     # output: past_key_values - key-value cache for next step
#     outputs = model(**inputs)
#     # Get prediction of last position output from dimension [batch_size, vocab_size],e.g.[1,54782]
#     next_token_logits = outputs.logits[:, -1, :]
#     # Do sampling for next token(convert to possibility value between [0,1])
#     probs = torch.softmax(next_token_logits, dim=-1)
#     # random get 1 sample with this possibility(not use argmax:get max possibility sample)
#     next_token_id = torch.multinomial(probs, num_samples=1)
#     # Convert to text from token vector
#     print(tokenizer.decode(next_token_id[0]))

# Method2(Recommended): Automatic generation token
# outputs = model.generate(
#     **inputs,
#     max_new_tokens=20,
#     do_sample=True,
#     temperature=0.7,
#     top_p=0.9
# )
# generated_text = tokenizer.decode(outputs[0])
# print(generated_text)

# =========Phase 2: Prepare model and tokenizer for Reasoning =========
prompt = 'Please speak a joke?'
messages = [
    {'role':'system', 'content': 'You are Qwen, created by Alibaba Cloud. You are a helpful assistant.'},
    {'role':'user', 'content': prompt}
]

text = tokenizer.apply_chat_template(
    messages,
    tokenizer=False,
    add_generation_prompt= True
)
model_inputs = tokenizer([text], return_tensors='pt').to(model.device)
print(text)
print('====' * 10)
# input_ids and attention_mask attribute
print(model_inputs)

# =========Phase 3: Reasoning and Decode =========
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)

generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids,generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)