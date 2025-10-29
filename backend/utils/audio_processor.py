import librosa
import numpy as np
import soundfile as sf
from pydub import AudioSegment
import os

class AudioProcessor:
    """Handle audio file processing and feature extraction"""
    
    def __init__(self, sample_rate=22050, hop_length=512):
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        
    def load_audio(self, file_path):
        """Load audio file and convert to appropriate format"""
        try:
            # Try loading directly with librosa
            y, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            return y, sr
        except Exception as e:
            # Try converting with pydub
            try:
                audio = AudioSegment.from_file(file_path)
                audio = audio.set_frame_rate(self.sample_rate).set_channels(1)
                
                # Export to temporary wav file
                temp_path = file_path + '_temp.wav'
                audio.export(temp_path, format='wav')
                
                y, sr = librosa.load(temp_path, sr=self.sample_rate)
                os.remove(temp_path)
                
                return y, sr
            except Exception as e2:
                raise Exception(f"Could not load audio file: {e2}")
    
    def extract_chromagram(self, y, sr):
        """Extract chromagram (pitch class distribution over time)"""
        chromagram = librosa.feature.chroma_cqt(
            y=y, 
            sr=sr, 
            hop_length=self.hop_length,
            n_chroma=12
        )
        return chromagram
    
    def extract_tempo_beats(self, y, sr):
        """Extract tempo and beat positions"""
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
        beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=self.hop_length)
        return float(tempo), beat_times
    
    def extract_onset_strength(self, y, sr):
        """Extract onset strength envelope"""
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
        return onset_env
    
    def extract_energy(self, y, sr):
        """Calculate overall energy of the signal"""
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)
        return float(np.mean(rms))
    
    def extract_spectral_features(self, y, sr):
        """Extract spectral features"""
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=self.hop_length)
        
        return {
            'centroid': float(np.mean(spectral_centroids)),
            'rolloff': float(np.mean(spectral_rolloff))
        }
    
    def separate_harmonic_percussive(self, y):
        """Separate harmonic and percussive components"""
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        return y_harmonic, y_percussive
    
    def extract_all_features(self, file_path):
        """Extract all relevant features from audio file"""
        # Load audio
        y, sr = self.load_audio(file_path)
        
        # Separate harmonic component for better chord detection
        y_harmonic, y_percussive = self.separate_harmonic_percussive(y)
        
        # Extract features
        chromagram = self.extract_chromagram(y_harmonic, sr)
        tempo, beat_times = self.extract_tempo_beats(y, sr)
        onset_env = self.extract_onset_strength(y, sr)
        energy = self.extract_energy(y, sr)
        spectral_features = self.extract_spectral_features(y, sr)
        
        # Calculate duration
        duration = librosa.get_duration(y=y, sr=sr)
        
        return {
            'y': y,
            'y_harmonic': y_harmonic,
            'y_percussive': y_percussive,
            'sr': sr,
            'chromagram': chromagram,
            'tempo': tempo,
            'beat_times': beat_times,
            'onset_env': onset_env,
            'energy': energy,
            'spectral_features': spectral_features,
            'duration': duration
        }