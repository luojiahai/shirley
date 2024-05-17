import torch
from generator import Generator

def main():
    print("Hello, World!")
    print()

    prompt = 'What is potato?'

    print("BEGIN PRINT PROMPT")
    print(prompt)
    print("END PRINT PROMPT")
    print()

    print("BEGIN GENERATION")
    generator = Generator(
        pretrained_model_name_or_path='models/Mistral-7B-Instruct-v0.2',
        local_files_only=True,
        torch_dtype=torch.bfloat16,
    )
    text_outputs = generator.generate(
        prompt=prompt,
        return_full_text=False,
        do_sample=True,
        pad_token_id=generator.tokenizer.eos_token_id,
        max_new_tokens=256,
    )
    print("END GENERATION")
    print()

    print("BEGIN PRINT GENERATED TEXT")
    print(text_outputs)
    print("END PRINT GENERATED TEXT")
    print()

if __name__ == "__main__":
    main()
