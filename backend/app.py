from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import traceback
from config import Config
from utils.audio_processor import AudioProcessor
from models.chord_detector import ChordDetector
from models.rhythm_analyzer import RhythmAnalyzer
from models.strumming_generator import StrummingGenerator
from utils.music_theory import MusicTheory

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize processors
audio_processor = AudioProcessor(
    sample_rate=Config.SAMPLE_RATE,
    hop_length=Config.HOP_LENGTH
)
chord_detector = ChordDetector(confidence_threshold=Config.CONFIDENCE_THRESHOLD)
rhythm_analyzer = RhythmAnalyzer()
strumming_generator = StrummingGenerator()
music_theory = MusicTheory()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('../frontend', path)

@app.route('/api/analyze', methods=['POST'])
def analyze_song():
    """
    Main endpoint for comprehensive guitar analysis
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: mp3, wav, ogg, flac, m4a'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Step 1: Extract audio features
        print("Extracting audio features...")
        features = audio_processor.extract_all_features(filepath)
        
        # Step 2: Detect chords, plucking, and solos
        print("Detecting chords, plucking patterns, and solos...")
        segments = chord_detector.detect_chords_and_patterns(
            features['chromagram'],
            features['beat_times'],
            features['sr'],
            audio_processor.hop_length,
            features['y'],
            features['y_harmonic']
        )
        
        formatted_segments = chord_detector.format_segments(segments)
        unique_chords = chord_detector.get_unique_chords(segments)
        
        # Step 3: Key detection
        print("Detecting key...")
        detected_key, key_confidence = music_theory.detect_key(unique_chords)
        key_confidence = float(key_confidence)
        scale_info = music_theory.get_scale_info(detected_key)
        
        # Step 4: Capo suggestions
        print("Analyzing capo options...")
        capo_suggestion = music_theory.suggest_capo(unique_chords, detected_key)
        
        # Step 5: Chord difficulty analysis
        print("Analyzing chord difficulty...")
        chord_difficulties = {chord: music_theory.get_chord_difficulty(chord) for chord in unique_chords}
        avg_difficulty = float(sum(chord_difficulties.values()) / len(chord_difficulties)) if chord_difficulties else 0.0
        
        # Step 6: Chord transition analysis
        print("Analyzing chord transitions...")
        transitions = music_theory.analyze_chord_transitions(unique_chords)
        
        # Step 7: Rhythm analysis
        print("Analyzing rhythm...")
        rhythm_info = rhythm_analyzer.analyze_rhythm(
            features['y'],
            features['sr'],
            features['tempo'],
            features['beat_times'],
            features['onset_env']
        )
        
        # Step 8: Comprehensive strumming analysis
        print("Generating comprehensive strumming analysis...")
        strumming_info = strumming_generator.generate_comprehensive_strumming_analysis(
            features['tempo'],
            features['energy'],
            rhythm_info['time_signature'],
            rhythm_info,
            unique_chords
        )
        
        # Step 9: Practice routine
        print("Generating practice routine...")
        practice_routine = strumming_generator.generate_practice_routine(
            unique_chords,
            features['tempo'],
            strumming_info['recommended']
        )
        
        # Step 10: Get chord fingerings
        print("Fetching chord fingerings...")
        chord_fingerings = {}
        for chord in unique_chords:
            if chord in music_theory.CHORD_FINGERINGS:
                chord_fingerings[chord] = music_theory.CHORD_FINGERINGS[chord]
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Calculate statistics
        total_chord_sections = int(len(formatted_segments['chord_sections']))
        total_plucking_sections = int(len(formatted_segments['plucking_sections']))
        total_solo_sections = int(len(formatted_segments['solo_sections']))
        
        # Prepare comprehensive response
        response = {
            'success': True,
            'song_info': {
                'duration': features['duration'],
                'tempo': features['tempo'],
                'time_signature': rhythm_info['time_signature'],
                'key': detected_key,
                'key_confidence': key_confidence,
                'energy': features['energy'],
                'groove': rhythm_info['groove'],
                'total_chord_sections': total_chord_sections,
                'total_plucking_sections': total_plucking_sections,
                'total_solo_sections': total_solo_sections,
                'avg_chord_difficulty': float(avg_difficulty)
            },
            'segments': formatted_segments,
            'unique_chords': unique_chords,
            'chord_analysis': {
                'difficulties': chord_difficulties,
                'transitions': transitions,
                'fingerings': chord_fingerings
            },
            'key_analysis': {
                'detected_key': detected_key,
                'confidence': float(key_confidence),
                'scale_info': scale_info
            },
            'capo_suggestion': capo_suggestion,
            'rhythm': rhythm_info,
            'strumming': strumming_info,
            'practice_routine': practice_routine
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error analyzing song: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': f'Error analyzing song: {str(e)}',
            'success': False
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Guitar Cover Assistant API is running'})

@app.route('/api/chord-details/<chord_name>', methods=['GET'])
def get_chord_details(chord_name):
    """
    Get detailed information about a specific chord
    """
    try:
        # Get chord fingering details
        chord_details = music_theory.get_chord_fingering_details(chord_name)
        
        if not chord_details:
            return jsonify({
                'success': False,
                'error': f'Chord details not found for {chord_name}'
            }), 404
        
        # Generate ASCII diagram
        diagram = music_theory.generate_chord_diagram(
            chord_details['frets'],
            chord_name
        )
        
        response = {
            'success': True,
            'chord_details': {
                'name': chord_name,
                'frets': chord_details['frets'],
                'fingers': chord_details['fingers'],
                'difficulty': chord_details['difficulty'],
                'description': chord_details.get('description', ''),
                'finger_details': chord_details.get('finger_details', {}),
                'tips': chord_details.get('tips', []),
                'common_transitions': chord_details.get('common_transitions', []),
                'barre': chord_details.get('barre', False),
                'diagram': diagram
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error getting chord details: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    Config.init_app(app)
    print("=" * 50)
    print("Guitar Cover Assistant - Starting Server")
    print("=" * 50)
    print(f"Server running at http://{Config.HOST}:{Config.PORT}")
    print("Upload a song to get comprehensive guitar analysis!")
    print("=" * 50)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)