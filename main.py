from generator import Generator

def main():
    print("Hello, World!")
    print()

    prompt = 'What is potato?'

    generator = Generator()
    text = generator.generate(prompt)

    print("BEGIN PRINT GENERATED TEXT")
    print(text)
    print("END PRINT GENERATED TEXT")
    print()

if __name__ == "__main__":
    main()
