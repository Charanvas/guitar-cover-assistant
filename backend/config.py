import os

class Config:
    # Server Configuration
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac', 'm4a'}
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    
    # Audio Processing Configuration
    SAMPLE_RATE = 22050
    HOP_LENGTH = 512
    N_FFT = 2048
    
    # Chord Detection Configuration
    CHORD_SMOOTH_WINDOW = 5
    CONFIDENCE_THRESHOLD = 0.6
    
    # Model Configuration
    MODEL_PATH = 'models_data'
    
    # Chord vocabulary
    CHORD_TYPES = ['maj', 'min', '7', 'maj7', 'min7', 'dim', 'aug', 'sus2', 'sus4']
    ROOT_NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.MODEL_PATH, exist_ok=True)