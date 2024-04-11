class FileHandler:
    def __init__(self, path='./query.tmp'):
        self.file_path = path
        with open(self.file_path, 'a') as file:
            pass

    def read(self):
        with open(self.file_path, 'r') as file:
            return file.read()

    def write(self, data):
        with open(self.file_path, 'a') as file:
            file.write(data)


if __name__ == "__main__":
    pass
