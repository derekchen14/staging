import runhouse as rh
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

def causal_lm_generate(utterances, model_id='google/flan-t5-xl', **model_kwargs):
    (tokenizer, model) = rh.get_pinned_object(model_id) or (None, None)

    if model is None:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_id).to('cuda')
        rh.pin_to_memory(model_id, (tokenizer, model))

    inputs = tokenizer(utterances, return_tensors="pt").to('cuda')
    # Generation options: https://huggingface.co/docs/transformers/main/en/main_classes/text_generation#transformers.GenerationConfig
    outputs = model.generate(**inputs, **model_kwargs)
    return tokenizer.batch_decode(outputs.detach().cpu().numpy(), skip_special_tokens=True)


def init_function():
    # The first time this runs it will take ~7 minutes to download the model. After that it takes ~4 seconds.
    gpu = rh.cluster(name='rh-a10x', instance_type='A10:1', provider='lambda')  #  or "A100:1"
    # gpu = rh.cluster(name='rh-a10x', ips=['some numbers'], ssh_user='some user')
    env_packages = ['local:./', 'matplotlib', 'numpy', 'torch', 'transformers', 'tokenizers', 'peft']
    return rh.function(fn=causal_lm_generate).to(gpu, env=env_packages)  # runs on RPC to the cluster


if __name__ == "__main__":
    model_generate = init_function()

    utterances = ["How many orders were placed by customers from California last month?",
            "Which marketing channel has the highest conversion rate?",
            "What is the breakdown of customer age groups for purchases over $100 in the last year?"]        

    sequences = model_generate(utterances, max_new_tokens=32, min_length=2, temperature=1.0, 
                                repetition_penalty=1.2, use_cache=False, do_sample=True, stream_logs=True)
    for utt, seq in zip(utterances, sequences):
        print(f"{utt} -> {seq}")

    # does the name have to match the variable?
    model_generate.save(name='flan_t5_generate')
    # rh.cluster(name='rh-a10x') if rh.exists('rh-a10x') else 