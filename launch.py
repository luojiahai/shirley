import os

def main():
    python_path = os.path.join(os.getcwd(), 'python')
    if os.path.exists(python_path):
        file_name = None
        for file in os.listdir(python_path):
            if file.endswith("._pth"):
                file_name = os.path.join(python_path, file)

        if file_name:
            data = None
            with open(file_name, 'r') as file:
                data = file.read() 
                if '.\n..\n' not in data:
                    data = data.replace('.\n', '.\n..\n') 
                if '#import site' in data:
                    data = data.replace('#import site', 'import site')
            with open(file_name, 'w') as file:
                file.write(data)

if __name__ == "__main__":
    main()
