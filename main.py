from app import App

def main():
    print("Hello, World!")
    print()

    app = App(model_path='models/Mistral-7B-Instruct-v0.2')
    decoded_sentences = app.generate(prompt='What is potato?')
    text = decoded_sentences[0]
    print(text)

if __name__ == "__main__":
    main()
