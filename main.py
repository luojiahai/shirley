from generator import Generator

def main():
    print('Hello, World!')
    print()

    prompt = 'What is potato?'

    print('BEGIN PRINT PROMPT')
    print(prompt)
    print('END PRINT PROMPT')
    print()

    print('BEGIN INITIALIZATION')
    generator = Generator()
    print('Device:', generator.device)
    print('END INITIALIZATION')
    print()

    print('BEGIN GENERATION')
    generated_text = generator.generate(prompt)
    print('END GENERATION')
    print()

    print('BEGIN PRINT GENERATED TEXT')
    print(generated_text)
    print('END PRINT GENERATED TEXT')
    print()

if __name__ == '__main__':
    main()
