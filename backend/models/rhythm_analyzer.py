import numpy as np
import librosa

class RhythmAnalyzer:
    """Analyze rhythm and timing characteristics"""
    
    def __init__(self):
        pass
    
    def analyze_rhythm(self, y, sr, tempo, beat_times, onset_env):
        """
        Analyze rhythmic characteristics of the song
        """
        # Detect time signature
        time_signature = self._estimate_time_signature(beat_times)
        
        # Calculate beat strength
        beat_strength = self._calculate_beat_strength(onset_env, beat_times, sr)
        
        # Identify strong beats (downbeats)
        downbeats = self._identify_downbeats(beat_strength, time_signature)
        
        # Calculate rhythmic complexity
        complexity = self._calculate_rhythmic_complexity(onset_env)
        
        # Determine groove type
        groove = self._determine_groove(tempo, beat_strength, complexity)
        
        return {
            'tempo': float(tempo),
            'time_signature': time_signature,
            'beat_strength': beat_strength.tolist() if isinstance(beat_strength, np.ndarray) else beat_strength,
            'downbeats': downbeats,
            'complexity': float(complexity),
            'groove': groove
        }
    
    def _estimate_time_signature(self, beat_times):
        """Estimate time signature from beat intervals"""
        if len(beat_times) < 4:
            return '4/4'  # Default
        
        # Calculate intervals between beats
        intervals = np.diff(beat_times)
        
        # Most songs are in 4/4, 3/4, or 6/8
        # Look for patterns in beat groupings
        median_interval = np.median(intervals)
        
        # Simple heuristic: assume 4/4 for most cases
        # More sophisticated analysis would be needed for accurate detection
        return '4/4'
    
    def _calculate_beat_strength(self, onset_env, beat_times, sr, hop_length=512):
        """Calculate strength of each beat"""
        beat_frames = librosa.time_to_frames(beat_times, sr=sr, hop_length=hop_length)
        beat_strength = []
        
        for frame in beat_frames:
            if frame < len(onset_env):
                # Get strength in window around beat
                window = 5
                start = max(0, frame - window)
                end = min(len(onset_env), frame + window)
                strength = np.mean(onset_env[start:end])
                beat_strength.append(float(strength))
            else:
                beat_strength.append(0.0)
        
        return np.array(beat_strength)
    
    def _identify_downbeats(self, beat_strength, time_signature):
        """Identify downbeats (strong beats)"""
        # Parse time signature
        beats_per_bar = int(time_signature.split('/')[0])
        
        downbeats = []
        for i in range(0, len(beat_strength), beats_per_bar):
            downbeats.append(i)
        
        return downbeats
    
    def _calculate_rhythmic_complexity(self, onset_env):
        """Calculate overall rhythmic complexity"""
        # Use variance and entropy as measures
        variance = np.var(onset_env)
        
        # Normalize to 0-1 range
        complexity = min(1.0, variance / 10.0)
        
        return complexity
    
    def _determine_groove(self, tempo, beat_strength, complexity):
        """Determine the groove/feel of the song"""
        avg_strength = np.mean(beat_strength) if len(beat_strength) > 0 else 0.5
        
        if tempo < 70:
            return 'Slow/Ballad'
        elif tempo < 100:
            if complexity < 0.3:
                return 'Moderate/Relaxed'
            else:
                return 'Moderate/Syncopated'
        elif tempo < 130:
            if avg_strength > 0.6:
                return 'Upbeat/Driving'
            else:
                return 'Medium/Steady'
        else:
            if complexity > 0.6:
                return 'Fast/Complex'
            else:
                return 'Fast/Energetic'
        