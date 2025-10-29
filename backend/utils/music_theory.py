import numpy as np

class MusicTheory:
    """Enhanced music theory utilities for comprehensive guitar analysis"""
    
    # Note names
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Chord templates (semitone intervals from root)
    CHORD_TEMPLATES = {
        'maj': [0, 4, 7],
        'min': [0, 3, 7],
        '7': [0, 4, 7, 10],
        'maj7': [0, 4, 7, 11],
        'min7': [0, 3, 7, 10],
        'dim': [0, 3, 6],
        'aug': [0, 4, 8],
        'sus2': [0, 2, 7],
        'sus4': [0, 5, 7],
        '6': [0, 4, 7, 9],
        'min6': [0, 3, 7, 9],
        '9': [0, 4, 7, 10, 14],
        'add9': [0, 4, 7, 14],
        'm7b5': [0, 3, 6, 10],
        'dim7': [0, 3, 6, 9],
    }
    
    # Key signatures with their chords
    KEY_SIGNATURES = {
        'C': ['C', 'Dm', 'Em', 'F', 'G', 'Am', 'Bdim'],
        'G': ['G', 'Am', 'Bm', 'C', 'D', 'Em', 'F#dim'],
        'D': ['D', 'Em', 'F#m', 'G', 'A', 'Bm', 'C#dim'],
        'A': ['A', 'Bm', 'C#m', 'D', 'E', 'F#m', 'G#dim'],
        'E': ['E', 'F#m', 'G#m', 'A', 'B', 'C#m', 'D#dim'],
        'F': ['F', 'Gm', 'Am', 'Bb', 'C', 'Dm', 'Edim'],
        'Am': ['Am', 'Bdim', 'C', 'Dm', 'Em', 'F', 'G'],
        'Em': ['Em', 'F#dim', 'G', 'Am', 'Bm', 'C', 'D'],
        'Dm': ['Dm', 'Edim', 'F', 'Gm', 'Am', 'Bb', 'C'],
    }
    
    # Chord difficulty ratings (1=easiest, 10=hardest)
    CHORD_DIFFICULTY = {
        'C': 1, 'G': 2, 'D': 2, 'A': 2, 'E': 2, 'Am': 1, 'Em': 1, 'Dm': 2,
        'F': 4, 'B': 5, 'Bb': 4, 'F#': 5, 'C#': 5, 'G#': 5,
        'Cmaj7': 3, 'Gmaj7': 3, 'Dmaj7': 3, 'Amaj7': 4, 'Emaj7': 4,
        'Am7': 2, 'Em7': 2, 'Dm7': 3, 'C7': 3, 'G7': 3, 'D7': 3, 'A7': 3, 'E7': 2,
        'Bm': 4, 'F#m': 4, 'C#m': 5, 'Gm': 3,
        'Cadd9': 3, 'Gadd9': 3, 'Dadd9': 3,
        'Fsus4': 3, 'Csus4': 2, 'Gsus4': 2, 'Dsus4': 2, 'Asus4': 2,
    }
    
    # Common strumming patterns (enhanced)
    # Comprehensive strumming patterns database
    STRUMMING_PATTERNS = {
        'basic': {
            'pattern': 'D D U U D U',
            'name': 'Basic Down-Up',
            'difficulty': 'Easy',
            'description': 'Most common beginner pattern',
            'bpm_range': [80, 140],
            'energy_range': [0.4, 0.8],
            'genres': ['Pop', 'Rock', 'Folk'],
            'best_for': 'General purpose, very versatile'
        },
        'folk': {
            'pattern': 'D D U D U',
            'name': 'Folk Strum',
            'difficulty': 'Easy',
            'description': 'Classic folk/country pattern',
            'bpm_range': [80, 120],
            'energy_range': [0.2, 0.6],
            'genres': ['Folk', 'Country', 'Acoustic'],
            'best_for': 'Acoustic ballads, singer-songwriter'
        },
        'ballad': {
            'pattern': 'D - D U - U D U',
            'name': 'Ballad',
            'difficulty': 'Medium',
            'description': 'Slow, emotional songs with space',
            'bpm_range': [50, 80],
            'energy_range': [0.1, 0.4],
            'genres': ['Ballad', 'Pop', 'Rock'],
            'best_for': 'Slow love songs, emotional pieces'
        },
        'pop': {
            'pattern': 'D D U U D -',
            'name': 'Pop Strum',
            'difficulty': 'Medium',
            'description': 'Modern pop songs',
            'bpm_range': [100, 130],
            'energy_range': [0.5, 0.8],
            'genres': ['Pop', 'Indie'],
            'best_for': 'Modern pop hits'
        },
        'reggae': {
            'pattern': '- - U - - U',
            'name': 'Reggae',
            'difficulty': 'Medium',
            'description': 'Upbeat reggae feel, offbeat emphasis',
            'bpm_range': [75, 95],
            'energy_range': [0.4, 0.7],
            'genres': ['Reggae', 'Ska'],
            'best_for': 'Laid-back grooves'
        },
        'funk': {
            'pattern': 'D x U x D U',
            'name': 'Funk Strum',
            'difficulty': 'Hard',
            'description': 'Percussive, muted strums (x = muted)',
            'bpm_range': [90, 120],
            'energy_range': [0.6, 1.0],
            'genres': ['Funk', 'Soul', 'R&B'],
            'best_for': 'Groovy, rhythmic songs'
        },
        'country': {
            'pattern': 'D - D U D - D U',
            'name': 'Country',
            'difficulty': 'Medium',
            'description': 'Classic country picking style',
            'bpm_range': [90, 130],
            'energy_range': [0.4, 0.7],
            'genres': ['Country', 'Folk'],
            'best_for': 'Country and bluegrass'
        },
        'rock': {
            'pattern': 'D D D U D U',
            'name': 'Rock Strum',
            'difficulty': 'Medium',
            'description': 'Driving rock rhythm',
            'bpm_range': [110, 160],
            'energy_range': [0.6, 1.0],
            'genres': ['Rock', 'Alternative'],
            'best_for': 'Driving rock songs'
        },
        'waltz': {
            'pattern': 'D - - D - -',
            'name': 'Waltz (3/4)',
            'difficulty': 'Easy',
            'description': 'Three-beat waltz pattern',
            'bpm_range': [60, 110],
            'energy_range': [0.2, 0.6],
            'genres': ['Waltz', 'Classical', 'Folk'],
            'best_for': '3/4 time signatures'
        },
        'calypso': {
            'pattern': 'D - U D - U',
            'name': 'Calypso',
            'difficulty': 'Medium',
            'description': 'Caribbean rhythm with bounce',
            'bpm_range': [90, 115],
            'energy_range': [0.5, 0.8],
            'genres': ['Calypso', 'Island', 'Tropical'],
            'best_for': 'Island vibes, tropical songs'
        },
        'sixteen_beat': {
            'pattern': 'D D U D D U D U',
            'name': '16th Note Pattern',
            'difficulty': 'Hard',
            'description': 'Fast, complex pattern',
            'bpm_range': [120, 160],
            'energy_range': [0.7, 1.0],
            'genres': ['Rock', 'Pop-punk', 'Metal'],
            'best_for': 'Fast-paced energetic songs'
        },
        'motown': {
            'pattern': 'D - U - D U - U',
            'name': 'Motown',
            'difficulty': 'Medium',
            'description': 'Classic soul and R&B groove',
            'bpm_range': [100, 130],
            'energy_range': [0.5, 0.8],
            'genres': ['Soul', 'R&B', 'Motown'],
            'best_for': '60s soul, R&B classics'
        },
        'shuffle': {
            'pattern': 'D - U D - U',
            'name': 'Shuffle',
            'difficulty': 'Medium',
            'description': 'Swung eighth note feel',
            'bpm_range': [80, 130],
            'energy_range': [0.4, 0.7],
            'genres': ['Blues', 'Jazz', 'Swing'],
            'best_for': 'Swing feel, blues'
        },
        'old_time': {
            'pattern': 'D D U - D U',
            'name': 'Old Time',
            'difficulty': 'Easy',
            'description': 'Traditional folk pattern',
            'bpm_range': [90, 130],
            'energy_range': [0.3, 0.6],
            'genres': ['Folk', 'Old-time', 'Bluegrass'],
            'best_for': 'Traditional folk music'
        },
        'boom_chick': {
            'pattern': 'D - U - D - U -',
            'name': 'Boom-Chick',
            'difficulty': 'Medium',
            'description': 'Bass-chord alternation',
            'bpm_range': [70, 110],
            'energy_range': [0.3, 0.6],
            'genres': ['Country', 'Folk', 'Bluegrass'],
            'best_for': 'Walking bass lines'
        },
        'fast_folk': {
            'pattern': 'D U D U D U D U',
            'name': 'Fast Folk',
            'difficulty': 'Medium',
            'description': 'Rapid alternating strums',
            'bpm_range': [130, 180],
            'energy_range': [0.5, 0.8],
            'genres': ['Folk', 'Celtic', 'Bluegrass'],
            'best_for': 'Fast Celtic and bluegrass tunes'
        },
        'bossa_nova': {
            'pattern': 'D - - U - D - U',
            'name': 'Bossa Nova',
            'difficulty': 'Hard',
            'description': 'Latin jazz rhythm',
            'bpm_range': [110, 140],
            'energy_range': [0.4, 0.7],
            'genres': ['Bossa Nova', 'Latin', 'Jazz'],
            'best_for': 'Latin jazz, smooth grooves'
        },
        'train_beat': {
            'pattern': 'D D U D D D U D',
            'name': 'Train Beat',
            'difficulty': 'Hard',
            'description': 'Driving locomotive rhythm',
            'bpm_range': [120, 160],
            'energy_range': [0.6, 0.9],
            'genres': ['Folk', 'Bluegrass', 'Country'],
            'best_for': 'Driving rhythm, train songs'
        },
        'island': {
            'pattern': 'D - U - D U - -',
            'name': 'Island Strum',
            'difficulty': 'Easy',
            'description': 'Relaxed island feel',
            'bpm_range': [80, 110],
            'energy_range': [0.3, 0.6],
            'genres': ['Reggae', 'Island', 'Tropical'],
            'best_for': 'Beach songs, relaxed vibes'
        },
        'skiffle': {
            'pattern': 'D U D - D U D -',
            'name': 'Skiffle',
            'difficulty': 'Medium',
            'description': 'Bouncy, rhythmic pattern',
            'bpm_range': [110, 140],
            'energy_range': [0.5, 0.8],
            'genres': ['Skiffle', 'Folk', 'Jazz'],
            'best_for': 'Bouncy, rhythmic songs'
        },
        'half_time': {
            'pattern': 'D - - - U - - -',
            'name': 'Half Time',
            'difficulty': 'Easy',
            'description': 'Very slow, sparse pattern',
            'bpm_range': [40, 70],
            'energy_range': [0.1, 0.3],
            'genres': ['Ballad', 'Ambient', 'Slow'],
            'best_for': 'Very slow ballads'
        },
        'bluegrass': {
            'pattern': 'D U D U - U D U',
            'name': 'Bluegrass',
            'difficulty': 'Hard',
            'description': 'Fast bluegrass rhythm',
            'bpm_range': [140, 200],
            'energy_range': [0.6, 0.9],
            'genres': ['Bluegrass', 'Country', 'Folk'],
            'best_for': 'Fast bluegrass picking'
        },
        'flamenco': {
            'pattern': 'D U D U D - U -',
            'name': 'Flamenco',
            'difficulty': 'Hard',
            'description': 'Spanish flamenco rhythm',
            'bpm_range': [100, 140],
            'energy_range': [0.6, 0.9],
            'genres': ['Flamenco', 'Spanish', 'Latin'],
            'best_for': 'Spanish guitar style'
        },
        'straight_eight': {
            'pattern': 'D U D U D U D U',
            'name': 'Straight Eighth Notes',
            'difficulty': 'Medium',
            'description': 'Even eighth note strumming',
            'bpm_range': [100, 150],
            'energy_range': [0.5, 0.8],
            'genres': ['Rock', 'Pop', 'Any'],
            'best_for': 'Steady, driving rhythm'
        },
        'syncopated': {
            'pattern': 'D - U D - U D -',
            'name': 'Syncopated',
            'difficulty': 'Hard',
            'description': 'Off-beat emphasis',
            'bpm_range': [90, 130],
            'energy_range': [0.5, 0.8],
            'genres': ['Funk', 'Reggae', 'Jazz'],
            'best_for': 'Syncopated rhythms'
        },
        'march': {
            'pattern': 'D - D - D - D -',
            'name': 'March Time',
            'difficulty': 'Easy',
            'description': 'Strong quarter note pulse',
            'bpm_range': [100, 130],
            'energy_range': [0.4, 0.7],
            'genres': ['March', 'Military', 'Polka'],
            'best_for': 'March tempo songs'
        },
        'arpeggiated': {
            'pattern': 'T 1 2 3 2 1 T 1',
            'name': 'Arpeggiated Strum',
            'difficulty': 'Medium',
            'description': 'Broken chord pattern',
            'bpm_range': [60, 100],
            'energy_range': [0.2, 0.5],
            'genres': ['Classical', 'Fingerstyle', 'Ballad'],
            'best_for': 'Gentle, flowing songs'
        },
        'triplet': {
            'pattern': 'D U D D U D',
            'name': 'Triplet Feel',
            'difficulty': 'Hard',
            'description': 'Three-note groupings',
            'bpm_range': [80, 120],
            'energy_range': [0.4, 0.7],
            'genres': ['Blues', 'Jazz', 'Swing'],
            'best_for': 'Triplet-based rhythms'
        },
        'muted_funk': {
            'pattern': 'x D x U x D x U',
            'name': 'Muted Funk',
            'difficulty': 'Hard',
            'description': 'Heavy muting for percussive effect',
            'bpm_range': [90, 120],
            'energy_range': [0.7, 1.0],
            'genres': ['Funk', 'Disco', 'R&B'],
            'best_for': 'Funky, percussive grooves'
        },
        'picking_pattern': {
            'pattern': 'T 1 T 2 T 3 T 1',
            'name': 'Alternating Bass',
            'difficulty': 'Medium',
            'description': 'Travis-style picking',
            'bpm_range': [70, 110],
            'energy_range': [0.3, 0.6],
            'genres': ['Country', 'Folk', 'Blues'],
            'best_for': 'Fingerstyle country and folk'
        }
    }
    
    # Chord fingerings (fret positions for standard tuning E-A-D-G-B-E)
    CHORD_FINGERINGS = {
        'C': {'frets': 'x32010', 'fingers': '032010', 'difficulty': 1},
        'G': {'frets': '320003', 'fingers': '320004', 'difficulty': 2},
        'D': {'frets': 'xx0232', 'fingers': '000132', 'difficulty': 2},
        'A': {'frets': 'x02220', 'fingers': '002340', 'difficulty': 2},
        'E': {'frets': '022100', 'fingers': '023100', 'difficulty': 2},
        'Am': {'frets': 'x02210', 'fingers': '002310', 'difficulty': 1},
        'Em': {'frets': '022000', 'fingers': '023000', 'difficulty': 1},
        'Dm': {'frets': 'xx0231', 'fingers': '000231', 'difficulty': 2},
        'F': {'frets': '133211', 'fingers': '134211', 'difficulty': 4},
        'B': {'frets': 'x24442', 'fingers': '013331', 'difficulty': 5},
    }
    
    @staticmethod
    def detect_key(chords):
        """Detect the most likely key from chord progression"""
        if not chords:
            return 'C', 0.0
        
        # Count chord matches for each key
        key_scores = {}
        
        for key, key_chords in MusicTheory.KEY_SIGNATURES.items():
            score = 0
            for chord in chords:
                # Simple chord name (remove complexity)
                simple_chord = chord.replace('maj7', '').replace('min7', '').replace('7', '')
                simple_chord = simple_chord.replace('m', 'min') if simple_chord.endswith('m') else simple_chord
                
                if any(simple_chord.startswith(kc.replace('min', 'm')) for kc in key_chords):
                    score += 1
            
            if len(chords) > 0:
                key_scores[key] = score / len(chords)
        
        if not key_scores:
            return 'C', 0.0
        
        best_key = max(key_scores.items(), key=lambda x: x[1])
        return best_key[0], best_key[1]
    
    @staticmethod
    def suggest_capo(chords, detected_key):
        """Suggest capo position for easier playing"""
        difficult_chords = [c for c in chords if MusicTheory.get_chord_difficulty(c) > 3]
        
        if not difficult_chords:
            return {
                'position': 0,
                'reason': 'No capo needed - all chords are beginner-friendly',
                'difficulty_reduction': 0
            }
        
        # Check if capo would help
        capo_suggestions = []
        
        for capo_fret in range(1, 6):
            # Transpose chords down by capo position
            transposed_chords = [MusicTheory.transpose_chord(c, -capo_fret) for c in chords]
            new_difficulty = sum(MusicTheory.get_chord_difficulty(c) for c in transposed_chords) / len(transposed_chords)
            old_difficulty = sum(MusicTheory.get_chord_difficulty(c) for c in chords) / len(chords)
            
            if new_difficulty < old_difficulty:
                capo_suggestions.append({
                    'position': capo_fret,
                    'difficulty_reduction': old_difficulty - new_difficulty,
                    'new_chords': transposed_chords
                })
        
        if capo_suggestions:
            best_capo = max(capo_suggestions, key=lambda x: x['difficulty_reduction'])
            return {
                'position': best_capo['position'],
                'reason': f'Reduces difficulty by {best_capo["difficulty_reduction"]:.1f} points',
                'difficulty_reduction': best_capo['difficulty_reduction'],
                'new_chords': best_capo['new_chords']
            }
        
        return {
            'position': 0,
            'reason': 'Capo would not significantly reduce difficulty',
            'difficulty_reduction': 0
        }
    
    @staticmethod
    def transpose_chord(chord, semitones):
        """Transpose a chord by semitones"""
        # Extract root note
        root = chord[0]
        if len(chord) > 1 and chord[1] in ['#', 'b']:
            root = chord[:2]
        
        # Find current index
        try:
            current_idx = MusicTheory.NOTE_NAMES.index(root)
        except ValueError:
            return chord  # Can't transpose
        
        # Calculate new index
        new_idx = (current_idx + semitones) % 12
        new_root = MusicTheory.NOTE_NAMES[new_idx]
        
        # Replace root in chord
        return new_root + chord[len(root):]
    
    @staticmethod
    def get_chord_difficulty(chord):
        """Get difficulty rating for a chord"""
        # Try exact match first
        if chord in MusicTheory.CHORD_DIFFICULTY:
            return MusicTheory.CHORD_DIFFICULTY[chord]
        
        # Try without modifiers
        base_chord = chord.replace('maj7', '').replace('min7', '').replace('7', '')
        if base_chord in MusicTheory.CHORD_DIFFICULTY:
            return MusicTheory.CHORD_DIFFICULTY[base_chord] + 1  # Add 1 for complexity
        
        # Default difficulty
        return 5
    
    @staticmethod
    def analyze_chord_transitions(chords):
        """Analyze difficulty of transitions between chords"""
        if len(chords) < 2:
            return []
        
        transitions = []
        for i in range(len(chords) - 1):
            chord1 = chords[i]
            chord2 = chords[i + 1]
            
            difficulty = MusicTheory.calculate_transition_difficulty(chord1, chord2)
            transitions.append({
                'from': chord1,
                'to': chord2,
                'difficulty': difficulty,
                'tips': MusicTheory.get_transition_tips(chord1, chord2)
            })
        
        return transitions
    
    @staticmethod
    def calculate_transition_difficulty(chord1, chord2):
        """Calculate difficulty of transitioning between two chords"""
        # Get fingerings
        fingering1 = MusicTheory.CHORD_FINGERINGS.get(chord1, {}).get('fingers', '000000')
        fingering2 = MusicTheory.CHORD_FINGERINGS.get(chord2, {}).get('fingers', '000000')
        
        # Count finger movements
        movements = sum(1 for f1, f2 in zip(fingering1, fingering2) if f1 != f2 and f1 != '0' and f2 != '0')
        
        # Rate difficulty (1-10)
        if movements == 0:
            return 1
        elif movements <= 2:
            return 3
        elif movements <= 4:
            return 6
        else:
            return 9
    
    @staticmethod
    def get_transition_tips(chord1, chord2):
        """Get tips for specific chord transitions"""
        common_transitions = {
            ('C', 'G'): 'Keep your 3rd finger anchored on the 3rd fret',
            ('G', 'D'): 'Pivot on your 3rd finger',
            ('D', 'A'): 'Slide your fingers down one string',
            ('Am', 'C'): 'Add your 3rd finger to the 3rd fret',
            ('Em', 'C'): 'Lift your 1st and 2nd fingers',
        }
        
        return common_transitions.get((chord1, chord2), 'Practice slowly and focus on finger placement')
    
    @staticmethod
    def get_scale_info(key):
        """Get scale information for the detected key"""
        # Major scale pattern: W W H W W W H (W=whole step, H=half step)
        # Minor scale pattern: W H W W H W W
        
        root_idx = MusicTheory.note_to_index(key.replace('m', ''))
        is_minor = 'm' in key or key.endswith('m')
        
        if is_minor:
            intervals = [0, 2, 3, 5, 7, 8, 10]  # Natural minor
            scale_type = 'Natural Minor'
        else:
            intervals = [0, 2, 4, 5, 7, 9, 11]  # Major
            scale_type = 'Major'
        
        scale_notes = [MusicTheory.index_to_note((root_idx + interval) % 12) for interval in intervals]
        
        return {
            'key': key,
            'type': scale_type,
            'notes': scale_notes,
            'relative_key': MusicTheory.get_relative_key(key)
        }
    
    @staticmethod
    def get_relative_key(key):
        """Get relative major/minor key"""
        root_idx = MusicTheory.note_to_index(key.replace('m', ''))
        
        if 'm' in key or key.endswith('m'):
            # Minor to Major (up 3 semitones)
            relative_idx = (root_idx + 3) % 12
            return MusicTheory.index_to_note(relative_idx)
        else:
            # Major to Minor (down 3 semitones)
            relative_idx = (root_idx - 3) % 12
            return MusicTheory.index_to_note(relative_idx) + 'm'
    
    @staticmethod
    def get_chord_name(root_note, chord_type):
        """Generate full chord name"""
        return f"{root_note}{chord_type}"
    
    @staticmethod
    def get_chord_intervals(chord_type):
        """Get semitone intervals for a chord type"""
        return MusicTheory.CHORD_TEMPLATES.get(chord_type, [0, 4, 7])
    
    @staticmethod
    def note_to_index(note_name):
        """Convert note name to chromatic index"""
        note_clean = note_name.replace('m', '')
        return MusicTheory.NOTE_NAMES.index(note_clean)
    
    @staticmethod
    def index_to_note(index):
        """Convert chromatic index to note name"""
        return MusicTheory.NOTE_NAMES[index % 12]
    
    @staticmethod
    def create_chord_profile(root, chord_type):
        """Create binary chord profile for matching"""
        profile = np.zeros(12)
        intervals = MusicTheory.get_chord_intervals(chord_type)
        root_idx = MusicTheory.note_to_index(root)
        
        for interval in intervals:
            profile[(root_idx + interval) % 12] = 1
            
        return profile
    
    @staticmethod
    def get_strumming_pattern(tempo, energy, time_signature='4/4'):
        """Suggest strumming pattern based on song characteristics"""
        bpm = tempo
        
        # Special case for 3/4 time
        if time_signature == '3/4':
            return MusicTheory.STRUMMING_PATTERNS['waltz']
        
        # Slow ballad
        if bpm < 70 and energy < 0.4:
            return MusicTheory.STRUMMING_PATTERNS['ballad']
        
        # Reggae
        elif 75 <= bpm <= 90 and 0.4 <= energy <= 0.7:
            return MusicTheory.STRUMMING_PATTERNS['reggae']
        
        # Folk/Country
        elif 90 <= bpm <= 120 and energy < 0.6:
            return MusicTheory.STRUMMING_PATTERNS['folk']
        
        # Pop
        elif 100 <= bpm <= 130 and energy >= 0.6:
            return MusicTheory.STRUMMING_PATTERNS['pop']
        
        # Funk
        elif bpm > 100 and energy > 0.7:
            return MusicTheory.STRUMMING_PATTERNS['funk']
        
        # Rock
        elif bpm > 110 and energy > 0.65:
            return MusicTheory.STRUMMING_PATTERNS['rock']
        
        # Default to basic
        else:
            return MusicTheory.STRUMMING_PATTERNS['basic']
    
    @staticmethod
    def get_all_suitable_patterns(tempo, energy, time_signature='4/4'):
        """Get all suitable strumming patterns for the song"""
        suitable_patterns = []
        
        for pattern_key, pattern in MusicTheory.STRUMMING_PATTERNS.items():
            bpm_min, bpm_max = pattern['bpm_range']
            
            # Check if tempo is in range (with some tolerance)
            if bpm_min - 20 <= tempo <= bpm_max + 20:
                suitable_patterns.append(pattern)
        
        # Sort by suitability
        def calculate_suitability(pattern):
            bpm_min, bpm_max = pattern['bpm_range']
            bpm_center = (bpm_min + bpm_max) / 2
            tempo_diff = abs(tempo - bpm_center)
            return 1 / (1 + tempo_diff / 50)
        
        
        suitable_patterns.sort(key=calculate_suitability, reverse=True)
        return suitable_patterns[:5]  # Return top 5
    # Complete chord fingerings database with detailed information
    CHORD_FINGERINGS = {
        # Major Chords
        'C': {
            'frets': 'x32010',
            'fingers': '032010',
            'difficulty': 1,
            'description': 'C Major - Most common open chord',
            'finger_details': {
                '3rd_string': '3rd fret - Ring finger',
                '2nd_string': '2nd fret - Middle finger',
                '1st_string': '1st fret - Index finger'
            },
            'tips': [
                'Keep fingers curved and on fingertips',
                'Press strings just behind the fret',
                'Make sure open strings ring clearly',
                'Common beginner chord - practice daily'
            ],
            'common_transitions': ['Am', 'F', 'G', 'Em'],
            'barre': False
        },
        'G': {
            'frets': '320003',
            'fingers': '210003',
            'difficulty': 2,
            'description': 'G Major - Big, full sound',
            'finger_details': {
                '6th_string': '3rd fret - Middle finger',
                '5th_string': '2nd fret - Index finger',
                '1st_string': '3rd fret - Ring/Pinky finger'
            },
            'tips': [
                'Two common fingerings: ring or pinky on high E string',
                'Make sure to strum all 6 strings',
                'Keep fingers arched to avoid muting adjacent strings',
                'Very common in folk and rock music'
            ],
            'common_transitions': ['C', 'D', 'Em', 'Am'],
            'barre': False
        },
        'D': {
            'frets': 'xx0232',
            'fingers': '000132',
            'difficulty': 2,
            'description': 'D Major - Bright, open sound',
            'finger_details': {
                '3rd_string': '2nd fret - Index finger',
                '2nd_string': '3rd fret - Ring finger',
                '1st_string': '2nd fret - Middle finger'
            },
            'tips': [
                'Strum only the top 4 strings (D, G, B, E)',
                'Avoid hitting the low E and A strings',
                'Form a small triangle with your fingers',
                'Common in country and folk music'
            ],
            'common_transitions': ['A', 'G', 'Em', 'Bm'],
            'barre': False
        },
        'A': {
            'frets': 'x02220',
            'fingers': '002340',
            'difficulty': 2,
            'description': 'A Major - Powerful open chord',
            'finger_details': {
                '4th_string': '2nd fret - Index finger',
                '3rd_string': '2nd fret - Middle finger',
                '2nd_string': '2nd fret - Ring finger'
            },
            'tips': [
                'Strum from the A string down (5 strings)',
                'All three fingers on 2nd fret - keep them close together',
                'Alternative: use one finger to barre strings 2-4',
                'Very common in rock music'
            ],
            'common_transitions': ['D', 'E', 'Bm', 'F#m'],
            'barre': False
        },
        'E': {
            'frets': '022100',
            'fingers': '023100',
            'difficulty': 2,
            'description': 'E Major - Full, rich sound',
            'finger_details': {
                '5th_string': '2nd fret - Middle finger',
                '4th_string': '2nd fret - Ring finger',
                '3rd_string': '1st fret - Index finger'
            },
            'tips': [
                'Strum all 6 strings for full sound',
                'One of the easiest open chords',
                'Make sure fingers don\'t touch adjacent strings',
                'Foundation for many barre chords'
            ],
            'common_transitions': ['A', 'B7', 'C#m', 'Am'],
            'barre': False
        },
        'F': {
            'frets': '133211',
            'fingers': '134211',
            'difficulty': 4,
            'description': 'F Major - First barre chord most learn',
            'finger_details': {
                '6th_string': '1st fret - Index finger (barre)',
                '4th_string': '3rd fret - Ring finger',
                '3rd_string': '2nd fret - Middle finger',
                '2nd_string': '1st fret - Index finger (barre)',
                '1st_string': '1st fret - Index finger (barre)'
            },
            'tips': [
                'Index finger barres all strings on 1st fret',
                'Press with side of index finger, not flat',
                'Keep thumb behind neck for leverage',
                'Most difficult chord for beginners - practice daily',
                'Ensure all strings ring clearly'
            ],
            'common_transitions': ['C', 'G', 'Am', 'Dm'],
            'barre': True
        },
        
        # Minor Chords
        'Am': {
            'frets': 'x02210',
            'fingers': '002310',
            'difficulty': 1,
            'description': 'A Minor - Dark, melancholic sound',
            'finger_details': {
                '4th_string': '2nd fret - Middle finger',
                '3rd_string': '2nd fret - Ring finger',
                '2nd_string': '1st fret - Index finger'
            },
            'tips': [
                'Very similar to E chord shape',
                'Strum from A string down (5 strings)',
                'Very common in pop and rock',
                'Easy chord for beginners'
            ],
            'common_transitions': ['C', 'G', 'F', 'Dm'],
            'barre': False
        },
        'Em': {
            'frets': '022000',
            'fingers': '023000',
            'difficulty': 1,
            'description': 'E Minor - Easiest minor chord',
            'finger_details': {
                '5th_string': '2nd fret - Middle finger',
                '4th_string': '2nd fret - Ring finger'
            },
            'tips': [
                'Only two fingers needed',
                'Strum all 6 strings',
                'Easiest chord to play',
                'Very common in rock and metal'
            ],
            'common_transitions': ['G', 'D', 'C', 'Am'],
            'barre': False
        },
        'Dm': {
            'frets': 'xx0231',
            'fingers': '000231',
            'difficulty': 2,
            'description': 'D Minor - Sad, emotional sound',
            'finger_details': {
                '3rd_string': '2nd fret - Middle finger',
                '2nd_string': '3rd fret - Ring finger',
                '1st_string': '1st fret - Index finger'
            },
            'tips': [
                'Strum only top 4 strings (D, G, B, E)',
                'Similar shape to D major',
                'Keep fingers curved',
                'Common in minor key songs'
            ],
            'common_transitions': ['Am', 'C', 'G', 'F'],
            'barre': False
        },
        'Bm': {
            'frets': 'x24432',
            'fingers': '013421',
            'difficulty': 4,
            'description': 'B Minor - Common barre chord',
            'finger_details': {
                '5th_string': '2nd fret - Index finger',
                '4th_string': '4th fret - Ring finger',
                '3rd_string': '4th fret - Pinky finger',
                '2nd_string': '3rd fret - Middle finger',
                '1st_string': '2nd fret - Index finger'
            },
            'tips': [
                'Can use full barre on 2nd fret or partial barre',
                'Alternative: play as mini-barre on top 4 strings',
                'Keep ring and pinky close together',
                'Very common in key of D and G'
            ],
            'common_transitions': ['G', 'D', 'A', 'F#m'],
            'barre': True
        },
        
        # Seventh Chords
        'C7': {
            'frets': 'x32310',
            'fingers': '032410',
            'difficulty': 3,
            'description': 'C Dominant 7 - Blues and jazz sound',
            'finger_details': {
                '4th_string': '3rd fret - Ring finger',
                '3rd_string': '2nd fret - Middle finger',
                '2nd_string': '3rd fret - Pinky finger',
                '1st_string': '1st fret - Index finger'
            },
            'tips': [
                'Similar to C major with added 7th',
                'Creates tension that resolves to F',
                'Common in blues progressions',
                'Strum from A string'
            ],
            'common_transitions': ['F', 'G', 'Am'],
            'barre': False
        },
        'G7': {
            'frets': '320001',
            'fingers': '320001',
            'difficulty': 3,
            'description': 'G Dominant 7 - Classic blues chord',
            'finger_details': {
                '6th_string': '3rd fret - Middle finger',
                '5th_string': '2nd fret - Index finger',
                '1st_string': '1st fret - Ring finger'
            },
            'tips': [
                'Similar to G major with lowered 7th',
                'Resolves naturally to C',
                'Very common in blues and rock',
                'Strum all 6 strings'
            ],
            'common_transitions': ['C', 'D', 'Em'],
            'barre': False
        },
        'D7': {
            'frets': 'xx0212',
            'fingers': '000213',
            'difficulty': 2,
            'description': 'D Dominant 7 - Country and blues',
            'finger_details': {
                '3rd_string': '2nd fret - Middle finger',
                '2nd_string': '1st fret - Index finger',
                '1st_string': '2nd fret - Ring finger'
            },
            'tips': [
                'Strum top 4 strings only',
                'Very easy dominant 7th chord',
                'Resolves to G',
                'Common in country music'
            ],
            'common_transitions': ['G', 'A', 'Em'],
            'barre': False
        },
        'A7': {
            'frets': 'x02020',
            'fingers': '002030',
            'difficulty': 2,
            'description': 'A Dominant 7 - Versatile seventh',
            'finger_details': {
                '4th_string': '2nd fret - Middle finger',
                '2nd_string': '2nd fret - Ring finger'
            },
            'tips': [
                'Only two fingers needed',
                'Easy seventh chord',
                'Resolves to D',
                'Very common in blues'
            ],
            'common_transitions': ['D', 'E', 'Bm'],
            'barre': False
        },
        'E7': {
            'frets': '020100',
            'fingers': '020100',
            'difficulty': 2,
            'description': 'E Dominant 7 - Blues classic',
            'finger_details': {
                '5th_string': '2nd fret - Middle finger',
                '3rd_string': '1st fret - Index finger'
            },
            'tips': [
                'Only two fingers needed',
                'Very common in blues',
                'Resolves to A',
                'Strum all 6 strings'
            ],
            'common_transitions': ['A', 'Am', 'B7'],
            'barre': False
        },
        
        # Major 7 Chords
        'Cmaj7': {
            'frets': 'x32000',
            'fingers': '032000',
            'difficulty': 3,
            'description': 'C Major 7 - Jazz and pop sound',
            'finger_details': {
                '4th_string': '3rd fret - Ring finger',
                '3rd_string': '2nd fret - Middle finger'
            },
            'tips': [
                'Beautiful, dreamy sound',
                'Common in jazz and bossa nova',
                'Let open strings ring',
                'Very easy fingering'
            ],
            'common_transitions': ['Am7', 'Dm7', 'G7'],
            'barre': False
        },
        'Gmaj7': {
            'frets': '320002',
            'fingers': '320004',
            'difficulty': 3,
            'description': 'G Major 7 - Bright, sophisticated',
            'finger_details': {
                '6th_string': '3rd fret - Middle finger',
                '5th_string': '2nd fret - Index finger',
                '1st_string': '2nd fret - Ring finger'
            },
            'tips': [
                'Similar to G with added major 7th',
                'Sophisticated sound',
                'Common in modern pop',
                'Strum all 6 strings'
            ],
            'common_transitions': ['Cmaj7', 'Am7', 'D7'],
            'barre': False
        },
        'Dmaj7': {
            'frets': 'xx0222',
            'fingers': '000111',
            'difficulty': 3,
            'description': 'D Major 7 - Warm, jazzy',
            'finger_details': {
                '3rd_string': '2nd fret - Index finger',
                '2nd_string': '2nd fret - Middle finger',
                '1st_string': '2nd fret - Ring finger'
            },
            'tips': [
                'Three fingers on 2nd fret',
                'Can barre with one finger',
                'Strum top 4 strings only',
                'Common in jazz'
            ],
            'common_transitions': ['Gmaj7', 'Bm7', 'A7'],
            'barre': False
        },
        'Amaj7': {
            'frets': 'x02120',
            'fingers': '002140',
            'difficulty': 4,
            'description': 'A Major 7 - Rich, complex sound',
            'finger_details': {
                '4th_string': '2nd fret - Middle finger',
                '3rd_string': '1st fret - Index finger',
                '2nd_string': '2nd fret - Ring finger'
            },
            'tips': [
                'Compact finger positioning',
                'Strum from A string',
                'Common in R&B and soul',
                'Keep fingers close together'
            ],
            'common_transitions': ['Dmaj7', 'F#m7', 'E7'],
            'barre': False
        },
        'Emaj7': {
            'frets': '021100',
            'fingers': '021300',
            'difficulty': 3,
            'description': 'E Major 7 - Lush, full sound',
            'finger_details': {
                '4th_string': '1st fret - Index finger',
                '5th_string': '2nd fret - Middle finger'
            },
            'tips': [
                'Similar to E major',
                'Strum all 6 strings',
                'Very common in jazz',
                'Beautiful open sound'
            ],
            'common_transitions': ['Amaj7', 'C#m7', 'B7'],
            'barre': False
        },
        
        # Minor 7 Chords
        'Am7': {
            'frets': 'x02010',
            'fingers': '002010',
            'difficulty': 2,
            'description': 'A Minor 7 - Smooth, mellow',
            'finger_details': {
                '4th_string': '2nd fret - Middle finger',
                '2nd_string': '1st fret - Index finger'
            },
            'tips': [
                'Very easy, only two fingers',
                'Common in pop and jazz',
                'Strum from A string',
                'Great for beginners'
            ],
            'common_transitions': ['Dm7', 'G7', 'Cmaj7'],
            'barre': False
        },
        'Em7': {
            'frets': '020000',
            'fingers': '020000',
            'difficulty': 1,
            'description': 'E Minor 7 - Easiest seventh chord',
            'finger_details': {
                '5th_string': '2nd fret - Middle finger'
            },
            'tips': [
                'Only one finger needed!',
                'Easiest seventh chord',
                'Strum all 6 strings',
                'Very common in all genres'
            ],
            'common_transitions': ['Am7', 'Dmaj7', 'Cmaj7'],
            'barre': False
        },
        'Dm7': {
            'frets': 'xx0211',
            'fingers': '000211',
            'difficulty': 2,
            'description': 'D Minor 7 - Melancholic, jazzy',
            'finger_details': {
                '3rd_string': '2nd fret - Middle finger',
                '2nd_string': '1st fret - Index finger',
                '1st_string': '1st fret - Index finger'
            },
            'tips': [
                'Can barre 1st and 2nd strings',
                'Strum top 4 strings',
                'Common in minor progressions',
                'Smooth sound'
            ],
            'common_transitions': ['G7', 'Cmaj7', 'Am7'],
            'barre': False
        },
        
        # Sus Chords
        'Csus4': {
            'frets': 'x33010',
            'fingers': '034010',
            'difficulty': 2,
            'description': 'C Suspended 4 - Unresolved tension',
            'finger_details': {
                '4th_string': '3rd fret - Ring finger',
                '3rd_string': '3rd fret - Pinky finger',
                '1st_string': '1st fret - Index finger'
            },
            'tips': [
                'Creates tension that wants to resolve to C',
                'Common in rock intros',
                'Strum from A string',
                'Great for creating movement'
            ],
            'common_transitions': ['C', 'F', 'G'],
            'barre': False
        },
        'Dsus4': {
            'frets': 'xx0233',
            'fingers': '000134',
            'difficulty': 2,
            'description': 'D Suspended 4 - Bright suspension',
            'finger_details': {
                '3rd_string': '2nd fret - Index finger',
                '2nd_string': '3rd fret - Ring finger',
                '1st_string': '3rd fret - Pinky finger'
            },
            'tips': [
                'Resolves naturally to D',
                'Strum top 4 strings',
                'Very common in folk',
                'Easy to switch to/from D'
            ],
            'common_transitions': ['D', 'A', 'G'],
            'barre': False
        },
        'Asus4': {
            'frets': 'x02230',
            'fingers': '002340',
            'difficulty': 2,
            'description': 'A Suspended 4 - Open, ringing',
            'finger_details': {
                '4th_string': '2nd fret - Middle finger',
                '3rd_string': '2nd fret - Ring finger',
                '2nd_string': '3rd fret - Pinky finger'
            },
            'tips': [
                'Very common in rock and pop',
                'Resolves to A',
                'Strum from A string',
                'Full, open sound'
            ],
            'common_transitions': ['A', 'D', 'E'],
            'barre': False
        },
        'Esus4': {
            'frets': '022200',
            'fingers': '023400',
            'difficulty': 2,
            'description': 'E Suspended 4 - Powerful suspension',
            'finger_details': {
                '5th_string': '2nd fret - Middle finger',
                '4th_string': '2nd fret - Ring finger',
                '3rd_string': '2nd fret - Pinky finger'
            },
            'tips': [
                'Three fingers on 2nd fret',
                'Strum all 6 strings',
                'Resolves to E',
                'Common in rock'
            ],
            'common_transitions': ['E', 'A', 'B'],
            'barre': False
        },
        'Gsus4': {
            'frets': '320013',
            'fingers': '340014',
            'difficulty': 3,
            'description': 'G Suspended 4 - Full, resonant',
            'finger_details': {
                '6th_string': '3rd fret - Ring finger',
                '2nd_string': '1st fret - Index finger',
                '1st_string': '3rd fret - Pinky finger'
            },
            'tips': [
                'Strum all 6 strings',
                'Resolves to G',
                'Common in acoustic songs',
                'Wide finger stretch'
            ],
            'common_transitions': ['G', 'C', 'D'],
            'barre': False
        },
        
        # Add9 Chords
        'Cadd9': {
            'frets': 'x32030',
            'fingers': '032040',
            'difficulty': 3,
            'description': 'C Add 9 - Modern pop sound',
            'finger_details': {
                '4th_string': '3rd fret - Ring finger',
                '3rd_string': '2nd fret - Middle finger',
                '2nd_string': 'Open',
                '1st_string': '3rd fret - Pinky finger'
            },
            'tips': [
                'Very popular in modern music',
                'Richer sound than plain C',
                'Strum from A string',
                'Let open B string ring'
            ],
            'common_transitions': ['G', 'Am7', 'Dsus4'],
            'barre': False
        },
        'Gadd9': {
            'frets': '300003',
            'fingers': '200004',
            'difficulty': 3,
            'description': 'G Add 9 - Bright, open sound',
            'finger_details': {
                '6th_string': '3rd fret - Middle finger',
                '1st_string': '3rd fret - Ring finger'
            },
            'tips': [
                'Beautiful open sound',
                'Very common in indie music',
                'Strum all 6 strings',
                'Easy fingering'
            ],
            'common_transitions': ['Cadd9', 'Dsus4', 'Em7'],
            'barre': False
        },
        'Dadd9': {
            'frets': 'x54030',
            'fingers': '043020',
            'difficulty': 4,
            'description': 'D Add 9 - Jangly, bright',
            'finger_details': {
                '5th_string': '5th fret - Pinky finger',
                '4th_string': '4th fret - Ring finger',
                '2nd_string': '3rd fret - Middle finger'
            },
            'tips': [
                'Requires finger stretch',
                'Beautiful ringing sound',
                'Strum from A string',
                'Common in fingerstyle'
            ],
            'common_transitions': ['G', 'Bm', 'A'],
            'barre': False
        },
        
        # Additional common chords
        'B7': {
            'frets': 'x21202',
            'fingers': '021304',
            'difficulty': 3,
            'description': 'B Dominant 7 - Blues staple',
            'finger_details': {
                '5th_string': '2nd fret - Middle finger',
                '4th_string': '1st fret - Index finger',
                '3rd_string': '2nd fret - Ring finger',
                '1st_string': '2nd fret - Pinky finger'
            },
            'tips': [
                'Common in blues and folk',
                'Compact fingering',
                'Resolves to E',
                'Strum from A string'
            ],
            'common_transitions': ['E', 'Em', 'A'],
            'barre': False
        },
        'F#m': {
            'frets': '244222',
            'fingers': '134111',
            'difficulty': 5,
            'description': 'F# Minor - Full barre chord',
            'finger_details': {
                '6th_string': '2nd fret - Index barre',
                '5th_string': '4th fret - Ring finger',
                '4th_string': '4th fret - Pinky finger',
                '3rd_string': '2nd fret - Index barre',
                '2nd_string': '2nd fret - Index barre',
                '1st_string': '2nd fret - Index barre'
            },
            'tips': [
                'Full barre on 2nd fret',
                'Based on Em shape',
                'Very common in key of D and A',
                'Practice barre technique daily'
            ],
            'common_transitions': ['D', 'A', 'Bm', 'E'],
            'barre': True
        },
        'C#m': {
            'frets': 'x46654',
            'fingers': '013421',
            'difficulty': 5,
            'description': 'C# Minor - High barre chord',
            'finger_details': {
                '5th_string': '4th fret - Index finger',
                '4th_string': '6th fret - Ring finger',
                '3rd_string': '6th fret - Pinky finger',
                '2nd_string': '5th fret - Middle finger',
                '1st_string': '4th fret - Index finger'
            },
            'tips': [
                'Mini barre or full barre',
                'Common in key of A and E',
                'Keep fingers close together',
                'Build finger strength'
            ],
            'common_transitions': ['A', 'E', 'B', 'F#m'],
            'barre': True
        },
        'Bb': {
            'frets': 'x13331',
            'fingers': '014231',
            'difficulty': 5,
            'description': 'B Flat Major - Common barre',
            'finger_details': {
                '5th_string': '1st fret - Index finger',
                '4th_string': '3rd fret - Ring finger',
                '3rd_string': '3rd fret - Pinky finger',
                '2nd_string': '3rd fret - Pinky finger',
                '1st_string': '1st fret - Index finger'
            },
            'tips': [
                'Barre 1st fret with index',
                'Common in many pop songs',
                'Can be challenging for beginners',
                'Strum from A string'
            ],
            'common_transitions': ['F', 'C', 'Gm', 'Eb'],
            'barre': True
        },
        'Gm': {
            'frets': '355333',
            'fingers': '134111',
            'difficulty': 5,
            'description': 'G Minor - Full barre chord',
            'finger_details': {
                '6th_string': '3rd fret - Index barre',
                '5th_string': '5th fret - Ring finger',
                '4th_string': '5th fret - Pinky finger',
                '3rd_string': '3rd fret - Index barre',
                '2nd_string': '3rd fret - Index barre',
                '1st_string': '3rd fret - Index barre'
            },
            'tips': [
                'Full barre on 3rd fret',
                'Common in minor keys',
                'Build finger strength first',
                'Strum all 6 strings'
            ],
            'common_transitions': ['Bb', 'F', 'Cm', 'D7'],
            'barre': True
        }
    }
    
    @staticmethod
    def get_chord_fingering_details(chord):
        """Get complete fingering details for a chord"""
        # Try exact match
        if chord in MusicTheory.CHORD_FINGERINGS:
            return MusicTheory.CHORD_FINGERINGS[chord]
        
        # Try to find similar chord (e.g., "Cmaj" for "Cmaj7")
        for key in MusicTheory.CHORD_FINGERINGS.keys():
            if chord.startswith(key):
                return MusicTheory.CHORD_FINGERINGS[key]
        
        return None
    
    @staticmethod
    def generate_chord_diagram(frets_string, chord_name):
        """Generate ASCII art chord diagram"""
        diagram = f"\n{chord_name}\n"
        diagram += "  E A D G B e\n"
        diagram += "  ┌─┬─┬─┬─┬─┐\n"
        
        frets = frets_string
        max_fret = max([int(f) if f.isdigit() else 0 for f in frets])
        
        for fret_num in range(max(4, max_fret + 1)):
            line = f"{fret_num} "
            for i, fret_val in enumerate(frets):
                if fret_val == 'x':
                    if fret_num == 0:
                        line += "X "
                    else:
                        line += "│ "
                elif fret_val == '0':
                    if fret_num == 0:
                        line += "O "
                    else:
                        line += "│ "
                elif int(fret_val) == fret_num:
                    line += "● "
                else:
                    line += "│ "
            diagram += line + "\n"
        
        diagram += "  └─┴─┴─┴─┴─┘\n"
        return diagram
        
        