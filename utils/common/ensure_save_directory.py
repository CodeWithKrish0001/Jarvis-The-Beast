import os

def ensure_save_directory(filepath):
    try:
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        return False
