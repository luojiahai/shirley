import shirley

def main():
    print('Hello, World!')
    print()

    # vector_store = shirley.VectorStore()
    # vector_store.index('resources/resume.pdf')

    # print('BEGIN PROMPT AUGMENTATION')
    # augmentor = shirley.Augmentor()
    # query = 'Introduce Geoffrey Law. Which university he graduated from? What is his current job?'
    # prompt = augmentor.augment(query, vector_store)
    # print('END PROMPT AUGMENTATION')
    # print()

    prompt = 'What is potato?'

    print('BEGIN PRINT PROMPT')
    print(prompt)
    print('END PRINT PROMPT')
    print()

    print('BEGIN INITIALIZATION')
    generator = shirley.Generator()
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
