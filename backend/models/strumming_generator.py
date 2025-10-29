import numpy as np
from utils.music_theory import MusicTheory

class StrummingGenerator:
    """Enhanced strumming pattern generator with high accuracy detection"""
    
    def __init__(self):
        self.music_theory = MusicTheory()
    
    def generate_comprehensive_strumming_analysis(self, tempo, energy, time_signature, rhythm_info, chords):
        """
        Generate highly accurate strumming pattern analysis with comprehensive options
        """
        print(f"\n=== STRUMMING ANALYSIS DEBUG ===")
        print(f"Tempo: {tempo:.1f} BPM")
        print(f"Energy: {energy:.3f}")
        print(f"Time Signature: {time_signature}")
        print(f"Groove: {rhythm_info.get('groove', 'Unknown')}")
        print(f"Complexity: {rhythm_info.get('complexity', 0.5):.2f}")
        
        groove = rhythm_info.get('groove', 'Medium/Steady')
        complexity = rhythm_info.get('complexity', 0.5)
        
        # Get accurately matched pattern
        recommended_pattern = self._match_pattern_v2(tempo, energy, time_signature, groove, complexity)
        
        # Get all ranked suitable patterns
        all_ranked = self._get_all_ranked_patterns(tempo, energy, time_signature, groove, complexity)
        
        print(f"\nRecommended: {recommended_pattern['name']} (Score: {recommended_pattern.get('match_score', 0):.3f})")
        print(f"Top 5 alternatives:")
        for i, p in enumerate(all_ranked[:5]):
            print(f"  {i+1}. {p['name']} (Score: {p.get('suitability_score', 0):.3f})")
        
        # Remove recommended from alternatives
        alternatives = [p for p in all_ranked if p['name'] != recommended_pattern['name']][:5]
        
        # Generate fingerpicking if appropriate
        fingerpicking = None
        if self._should_use_fingerpicking(tempo, energy, complexity):
            fingerpicking = self._generate_fingerpicking_pattern(time_signature, chords)
        
        # Add timing notes
        recommended_with_notes = self._add_timing_notes(recommended_pattern, tempo, energy, groove)
        alternatives_with_notes = [self._add_timing_notes(p, tempo, energy, groove) for p in alternatives]
        
        return {
            'recommended': recommended_with_notes,
            'alternatives': alternatives_with_notes,
            'fingerpicking': fingerpicking,
            'strums_per_bar': self._calculate_strums_per_bar(recommended_pattern['pattern']),
            'suggested_genres': recommended_pattern['genres'],
            'tempo_analysis': self._analyze_tempo_for_strumming(tempo),
            'energy_analysis': self._analyze_energy_for_strumming(energy),
            'pattern_confidence': recommended_pattern.get('match_score', 0.8)
        }
    
    def _match_pattern_v2(self, tempo, energy, time_signature, groove, complexity):
        """
        Improved pattern matching with better differentiation between songs
        """
        # Special handling for 3/4 time
        if '3' in time_signature or time_signature == '3/4':
            pattern = self.music_theory.STRUMMING_PATTERNS['waltz'].copy()
            pattern['match_score'] = 0.95
            return pattern
        
        best_pattern = None
        best_score = 0.0
        all_scores = {}
        
        for pattern_name, pattern in self.music_theory.STRUMMING_PATTERNS.items():
            if pattern_name == 'waltz' and time_signature != '3/4':
                continue
            
            score = 0.0
            score_details = {}
            
            # TEMPO SCORING (35% weight)
            bpm_min, bpm_max = pattern['bpm_range']
            if bpm_min <= tempo <= bpm_max:
                # Perfect range - give full score
                center = (bpm_min + bpm_max) / 2
                distance_from_center = abs(tempo - center)
                range_size = bpm_max - bpm_min
                tempo_score = 1.0 - (distance_from_center / (range_size * 2))
            else:
                # Outside range - calculate penalty
                if tempo < bpm_min:
                    distance = bpm_min - tempo
                else:
                    distance = tempo - bpm_max
                tempo_score = max(0, 1.0 - (distance / 50.0))
            
            score += tempo_score * 0.35
            score_details['tempo'] = tempo_score * 0.35
            
            # ENERGY SCORING (35% weight)
            energy_min, energy_max = pattern['energy_range']
            if energy_min <= energy <= energy_max:
                # Perfect energy match
                energy_center = (energy_min + energy_max) / 2
                energy_distance = abs(energy - energy_center)
                energy_range = energy_max - energy_min
                energy_score = 1.0 - (energy_distance / (energy_range * 2)) if energy_range > 0 else 1.0
            else:
                # Outside range
                if energy < energy_min:
                    distance = energy_min - energy
                else:
                    distance = energy - energy_max
                energy_score = max(0, 1.0 - (distance / 0.4))
            
            score += energy_score * 0.35
            score_details['energy'] = energy_score * 0.35
            
            # GROOVE KEYWORD MATCHING (20% weight)
            groove_lower = groove.lower()
            
            groove_keywords = {
                'ballad': ['ballad', 'slow', 'emotional'],
                'half_time': ['very slow', 'ambient'],
                'folk': ['relaxed', 'moderate', 'folk', 'acoustic'],
                'old_time': ['traditional', 'folk'],
                'country': ['country', 'steady'],
                'boom_chick': ['walking', 'country'],
                'pop': ['upbeat', 'driving', 'modern'],
                'rock': ['driving', 'energetic', 'rock'],
                'sixteen_beat': ['fast', 'energetic'],
                'funk': ['syncopated', 'complex', 'groovy'],
                'muted_funk': ['funk', 'percussive'],
                'reggae': ['reggae', 'relaxed'],
                'island': ['island', 'tropical'],
                'motown': ['soul', 'r&b'],
                'shuffle': ['swing', 'blues'],
                'fast_folk': ['fast', 'celtic'],
                'bluegrass': ['bluegrass', 'fast'],
                'bossa_nova': ['latin', 'jazz'],
                'flamenco': ['spanish', 'flamenco'],
                'basic': ['general', 'any'],
                'basic_down': ['punk', 'simple']
            }
            
            groove_score = 0.3  # Default
            if pattern_name in groove_keywords:
                for keyword in groove_keywords[pattern_name]:
                    if keyword in groove_lower:
                        groove_score = 1.0
                        break
            
            score += groove_score * 0.20
            score_details['groove'] = groove_score * 0.20
            
            # COMPLEXITY MATCHING (10% weight)
            pattern_complexities = {
                'basic_down': 0.1,
                'march': 0.2,
                'half_time': 0.2,
                'basic': 0.2,
                'island': 0.3,
                'folk': 0.3,
                'old_time': 0.3,
                'ballad': 0.3,
                'straight_eight': 0.4,
                'pop': 0.5,
                'country': 0.5,
                'rock': 0.5,
                'boom_chick': 0.5,
                'arpeggiated': 0.5,
                'calypso': 0.6,
                'motown': 0.6,
                'shuffle': 0.6,
                'fast_folk': 0.6,
                'skiffle': 0.6,
                'reggae': 0.6,
                'picking_pattern': 0.7,
                'syncopated': 0.7,
                'triplet': 0.7,
                'funk': 0.8,
                'sixteen_beat': 0.8,
                'bossa_nova': 0.8,
                'train_beat': 0.8,
                'bluegrass': 0.9,
                'flamenco': 0.9,
                'muted_funk': 0.9
            }
            
            pattern_complexity = pattern_complexities.get(pattern_name, 0.5)
            complexity_diff = abs(pattern_complexity - complexity)
            complexity_score = 1.0 - complexity_diff
            
            score += complexity_score * 0.10
            score_details['complexity'] = complexity_score * 0.10
            
            all_scores[pattern_name] = {
                'total': score,
                'details': score_details
            }
            
            if score > best_score:
                best_score = score
                best_pattern = pattern.copy()
                best_pattern['match_score'] = score
                best_pattern['score_breakdown'] = score_details
        
        if best_pattern is None:
            best_pattern = self.music_theory.STRUMMING_PATTERNS['basic'].copy()
            best_pattern['match_score'] = 0.5
        
        # Debug: Show top 3 scoring patterns
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1]['total'], reverse=True)
        print(f"\nTop 3 pattern scores:")
        for i, (name, data) in enumerate(sorted_scores[:3]):
            print(f"  {i+1}. {name}: {data['total']:.3f} (T:{data['details'].get('tempo',0):.2f} E:{data['details'].get('energy',0):.2f} G:{data['details'].get('groove',0):.2f})")
        
        return best_pattern
    
    def _get_all_ranked_patterns(self, tempo, energy, time_signature, groove, complexity):
        """
        Get ALL patterns ranked by suitability
        """
        ranked_patterns = []
        
        for pattern_name, pattern in self.music_theory.STRUMMING_PATTERNS.items():
            if pattern_name == 'waltz' and time_signature != '3/4':
                continue
            
            pattern_copy = pattern.copy()
            
            # Calculate suitability score
            bpm_min, bpm_max = pattern['bpm_range']
            bpm_center = (bpm_min + bpm_max) / 2
            tempo_distance = abs(tempo - bpm_center)
            tempo_score = 1.0 / (1.0 + tempo_distance / 30.0)
            
            energy_min, energy_max = pattern['energy_range']
            energy_center = (energy_min + energy_max) / 2
            energy_distance = abs(energy - energy_center)
            energy_score = 1.0 / (1.0 + energy_distance / 0.3)
            
            combined_score = (tempo_score * 0.6) + (energy_score * 0.4)
            pattern_copy['suitability_score'] = combined_score
            
            ranked_patterns.append(pattern_copy)
        
        # Sort by score
        ranked_patterns.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return ranked_patterns
    
    def _should_use_fingerpicking(self, tempo, energy, complexity):
        """Determine if fingerpicking is appropriate"""
        return (tempo < 90 and energy < 0.5) or (complexity < 0.25 and tempo < 100)
    
    def _add_timing_notes(self, pattern, tempo, energy, groove):
        """Add comprehensive timing notes to pattern"""
        notes = []
        
        # Tempo-specific guidance
        if tempo < 60:
            notes.append("⏱️ Very slow tempo - Count: 1...2...3...4... (4 seconds per beat)")
            notes.append("💡 Focus on smooth, sustained strums")
        elif tempo < 80:
            notes.append(f"⏱️ Slow tempo ({int(tempo)} BPM) - Keep steady, don't rush")
            notes.append("💡 Use metronome to maintain consistency")
        elif tempo < 110:
            notes.append(f"⏱️ Moderate tempo ({int(tempo)} BPM) - Comfortable learning pace")
            notes.append("💡 Tap your foot on beats 1 and 3")
        elif tempo < 140:
            notes.append(f"⏱️ Upbeat tempo ({int(tempo)} BPM) - Maintain consistent speed")
            notes.append("💡 Start at 70% speed, gradually increase")
        else:
            notes.append(f"⏱️ Fast tempo ({int(tempo)} BPM) - Requires good technique")
            notes.append("💡 Practice at half speed first, use lighter pick attack")
        
        # Pattern notation explanation
        notes.append("\n📖 Pattern Notation:")
        notes.append("⬇️ 'D' = Downstroke (strum from thick to thin strings)")
        notes.append("⬆️ 'U' = Upstroke (strum from thin to thick strings)")
        
        if '-' in pattern['pattern']:
            notes.append("⏸️ '-' = Rest/pause (keep counting, no strum)")
        
        if 'x' in pattern['pattern']:
            notes.append("🤚 'x' = Muted strum (dampen strings with palm or touch lightly)")
            notes.append("💡 For palm mute: rest palm edge on strings near bridge")
        
        if 'T' in pattern['pattern']:
            notes.append("👍 'T' = Thumb plays bass note (usually root of chord)")
            notes.append("💡 '1,2,3' = Index, middle, ring fingers on treble strings")
        
        # Energy-based dynamics
        if energy < 0.3:
            notes.append("\n🎵 Dynamics: Low energy - Use soft, delicate touch")
            notes.append("💡 Strum closer to neck (12th fret area) for warmer, softer tone")
            notes.append("💡 Let chords ring and sustain")
        elif energy < 0.6:
            notes.append("\n🎵 Dynamics: Medium energy - Balanced, controlled playing")
            notes.append("💡 Strum over soundhole for balanced, natural tone")
            notes.append("💡 Maintain consistent volume throughout")
        else:
            notes.append("\n🎵 Dynamics: High energy - Strong, confident strumming")
            notes.append("💡 Strum closer to bridge for brighter, punchier tone")
            notes.append("💡 Use firm pick attack, emphasize downbeats")
        
        # Difficulty-based advice
        if pattern['difficulty'] == 'Easy':
            notes.append("\n✅ Difficulty: Beginner-friendly - Perfect for learning")
            notes.append("💡 Focus on keeping steady rhythm")
            notes.append("💡 Master this before moving to complex patterns")
        elif pattern['difficulty'] == 'Medium':
            notes.append("\n⚠️ Difficulty: Intermediate level - Some practice needed")
            notes.append("💡 Practice chord changes separately first")
            notes.append("💡 Master each strum direction before combining")
        else:
            notes.append("\n🔥 Difficulty: Advanced - Requires coordination and practice")
            notes.append("💡 Practice very slowly with metronome")
            notes.append("💡 Break pattern into smaller sections")
        
        # Pattern-specific tips
        pattern_name = pattern['name'].lower()
        if 'reggae' in pattern_name:
            notes.append("\n🎸 Reggae Style Tips:")
            notes.append("• Emphasize the upstrokes (offbeats)")
            notes.append("• Lay back slightly on the beat for authentic feel")
            notes.append("• Use choppy, staccato strums")
        elif 'funk' in pattern_name:
            notes.append("\n🎸 Funk Style Tips:")
            notes.append("• Keep rhythm tight and precise")
            notes.append("• Muted strums should be sharp and percussive")
            notes.append("• Emphasize the 'and' beats")
        elif 'ballad' in pattern_name:
            notes.append("\n🎸 Ballad Style Tips:")
            notes.append("• Let chords ring and breathe")
            notes.append("• Use smooth, flowing transitions")
            notes.append("• Focus on emotional expression")
        elif 'country' in pattern_name or 'bluegrass' in pattern_name:
            notes.append("\n🎸 Country/Bluegrass Style Tips:")
            notes.append("• Keep it bouncy and rhythmic")
            notes.append("• Emphasize bass notes on downbeats")
            notes.append("• Use alternating bass technique")
        elif 'rock' in pattern_name:
            notes.append("\n🎸 Rock Style Tips:")
            notes.append("• Strong, driving downstrokes")
            notes.append("• Maintain consistent energy")
            notes.append("• Accent beats 2 and 4 (backbeat)")
        elif 'folk' in pattern_name:
            notes.append("\n🎸 Folk Style Tips:")
            notes.append("• Natural, flowing rhythm")
            notes.append("• Let it breathe, don't rush")
            notes.append("• Focus on storytelling feel")
        elif 'bossa' in pattern_name or 'latin' in pattern_name:
            notes.append("\n🎸 Latin Style Tips:")
            notes.append("• Syncopated rhythm is key")
            notes.append("• Keep wrist loose and relaxed")
            notes.append("• Emphasize the clave pattern")
        
        # Best use case
        notes.append(f"\n🎯 Best For: {pattern.get('best_for', 'Various styles')}")
        notes.append(f"🎼 Genres: {', '.join(pattern['genres'])}")
        
        pattern_copy = pattern.copy()
        pattern_copy['timing_notes'] = notes
        return pattern_copy
    
    def _calculate_strums_per_bar(self, pattern_string):
        """Calculate number of strums per bar"""
        strums = pattern_string.split()
        return len([s for s in strums if s in ['D', 'U', 'd', 'u', 'x', 'T', '1', '2', '3']])
    
    def _analyze_tempo_for_strumming(self, tempo):
        """Detailed tempo analysis for strumming"""
        if tempo < 60:
            return {
                'category': 'Very Slow (< 60 BPM)',
                'guidance': 'Extremely slow - like a heartbeat at rest',
                'practice_tip': 'Use very long, deliberate strums. Count out loud to maintain timing.',
                'typical_styles': ['Ballads', 'Ambient', 'Meditation music'],
                'metronome_settings': f'Start at {int(tempo)}, focus on sustain'
            }
        elif tempo < 80:
            return {
                'category': 'Slow (60-80 BPM)',
                'guidance': 'Slow ballad tempo - maintain steady rhythm without rushing',
                'practice_tip': 'Practice with metronome. Focus on consistency over speed.',
                'typical_styles': ['Ballads', 'Blues', 'Soul'],
                'metronome_settings': f'{int(tempo)} BPM, count: 1-2-3-4'
            }
        elif tempo < 100:
            return {
                'category': 'Moderate Slow (80-100 BPM)',
                'guidance': 'Comfortable learning pace - ideal for beginners',
                'practice_tip': 'Perfect tempo for learning new patterns and chord changes.',
                'typical_styles': ['Folk', 'Country', 'Singer-songwriter'],
                'metronome_settings': f'{int(tempo)} BPM, comfortable walking pace'
            }
        elif tempo < 120:
            return {
                'category': 'Moderate (100-120 BPM)',
                'guidance': 'Standard comfortable tempo for most popular songs',
                'practice_tip': 'Most common tempo range. Great for practicing technique.',
                'typical_styles': ['Pop', 'Rock', 'R&B'],
                'metronome_settings': f'{int(tempo)} BPM, natural jogging pace'
            }
        elif tempo < 140:
            return {
                'category': 'Moderately Fast (120-140 BPM)',
                'guidance': 'Upbeat, energetic playing required',
                'practice_tip': 'Build speed gradually from {int(tempo * 0.7)} BPM.',
                'typical_styles': ['Pop', 'Rock', 'Indie'],
                'metronome_settings': f'{int(tempo)} BPM, increase by 5 BPM increments'
            }
        else:
            return {
                'category': 'Fast (140+ BPM)',
                'guidance': 'Challenging speed requiring experience and stamina',
                'practice_tip': f'Start at {int(tempo * 0.6)} BPM. Use lighter pick, relaxed grip.',
                'typical_styles': ['Punk', 'Metal', 'Fast rock'],
                'metronome_settings': f'{int(tempo)} BPM, requires endurance practice'
            }
    
    def _get_tempo_styles(self, tempo):
        """Get typical musical styles for given tempo"""
        if tempo < 70:
            return ['Ballad', 'Ambient', 'Meditation']
        elif tempo < 100:
            return ['Folk', 'Blues', 'Country']
        elif tempo < 130:
            return ['Pop', 'Rock', 'R&B']
        else:
            return ['Punk', 'Metal', 'Fast rock']
    
    def _analyze_energy_for_strumming(self, energy):
        """Detailed energy analysis for strumming dynamics"""
        if energy < 0.25:
            return {
                'category': 'Very Low Energy',
                'dynamics': 'Very soft, whisper-quiet playing',
                'technique': 'Fingerstyle or very light pick attack',
                'tip': 'Use minimal pressure, let strings ring naturally',
                'pick_recommendation': 'Thin pick (0.46-0.60mm) or use fingers',
                'strumming_position': 'Near or over the neck (12th-19th fret area)',
                'tone_description': 'Warm, mellow, intimate'
            }
        elif energy < 0.4:
            return {
                'category': 'Low Energy',
                'dynamics': 'Soft, gentle volume - controlled and delicate',
                'technique': 'Light touch, fingertips barely touching strings',
                'tip': 'Focus on clarity and sustain over volume',
                'pick_recommendation': 'Thin to medium pick (0.60-0.73mm)',
                'strumming_position': 'Closer to neck, around soundhole',
                'tone_description': 'Soft, clear, gentle'
            }
        elif energy < 0.6:
            return {
                'category': 'Medium Energy',
                'dynamics': 'Balanced, moderate volume - standard playing',
                'technique': 'Standard pick attack with even pressure',
                'tip': 'Maintain consistent volume throughout the song',
                'pick_recommendation': 'Medium pick (0.73-0.88mm)',
                'strumming_position': 'Over soundhole for balanced tone',
                'tone_description': 'Balanced, natural, versatile'
            }
        elif energy < 0.8:
            return {
                'category': 'High Energy',
                'dynamics': 'Strong, driving rhythm with power',
                'technique': 'Firm pick attack, emphasize downbeats strongly',
                'tip': 'Use confident strokes, commit fully to each strum',
                'pick_recommendation': 'Medium-heavy pick (0.88-1.0mm)',
                'strumming_position': 'Closer to bridge for punch and brightness',
                'tone_description': 'Bright, powerful, cutting'
            }
        else:
            return {
                'category': 'Very High Energy',
                'dynamics': 'Powerful, aggressive, maximum intensity',
                'technique': 'Heavy attack with full arm motion, strong emphasis',
                'tip': 'Full commitment to each strum, use entire arm movement',
                'pick_recommendation': 'Heavy pick (1.0mm+) or extra heavy (1.5mm+)',
                'strumming_position': 'At or near bridge for maximum attack',
                'tone_description': 'Aggressive, punchy, intense'
            }
    
    def _generate_fingerpicking_pattern(self, time_signature, chords):
        """Generate detailed fingerpicking pattern with comprehensive instructions"""
        if '3' in time_signature or time_signature == '3/4':
            return {
                'pattern': 'T 1 2 3 2 1',
                'name': 'Waltz Fingerpicking',
                'difficulty': 'Medium',
                'description': 'Classic 3/4 waltz fingerpicking pattern - elegant and flowing',
                'notation_detail': {
                    'T': 'Thumb plays bass note (root of chord) on beat 1',
                    '1': 'Index finger plucks 3rd string (G string)',
                    '2': 'Middle finger plucks 2nd string (B string)',
                    '3': 'Ring finger plucks 1st string (high E string)'
                },
                'tips': [
                    'Thumb provides steady bass pulse on beat 1 of each measure',
                    'Fingers create flowing melody on beats 2 and 3',
                    'Let all notes ring together for full, rich sound',
                    'Practice thumb independently for 5 minutes before adding fingers',
                    'Keep thumb motion consistent - it\'s your metronome',
                    'Common in classical waltzes and folk music',
                    'Curl fingers slightly for better string contact'
                ],
                'tab_example': """
E|-----0-------0-------0-------|
B|---1---1---1---1---1---1-----|
G|-0-------0-------0-----------|
D|-----------------------------|
A|-----------------------------|
E|-0---------------------------|
  1   2   3   1   2   3   1   2
  T   1   2   3   2   1   T   1
(C chord example - 3/4 time)
""",
                'practice_steps': [
                    '1. Practice thumb alone for 2 minutes',
                    '2. Add index finger (thumb + 1)',
                    '3. Add middle finger (thumb + 1 + 2)',
                    '4. Add ring finger for complete pattern',
                    '5. Practice at 50% tempo first'
                ]
            }
        else:
            return {
                'pattern': 'T 1 2 3 1 2 3 1',
                'name': 'Travis Picking',
                'difficulty': 'Hard',
                'description': 'Classic alternating bass Travis picking pattern - foundation of country and folk',
                'notation_detail': {
                    'T': 'Thumb alternates between root (usually 6th, 5th, or 4th string) and 5th of chord',
                    '1': 'Index finger consistently plucks 3rd string (G string)',
                    '2': 'Middle finger consistently plucks 2nd string (B string)',
                    '3': 'Ring finger consistently plucks 1st string (high E string)'
                },
                'tips': [
                    'Thumb maintains steady alternating bass: Root - 5th - Root - 5th',
                    'Bass pattern continues regardless of what fingers do',
                    'Fingers pluck in consistent rolling pattern: 1-2-3-1-2-3',
                    'Practice thumb bass pattern alone for 10 minutes minimum',
                    'Add one finger at a time over several practice sessions',
                    'Keep thumb and fingers completely independent',
                    'Common in country, folk, blues, and fingerstyle',
                    'Named after Merle Travis, country guitar legend',
                    'Once mastered, works with any chord',
                    'Thumb provides rhythm, fingers provide melody'
                ],
                'tab_example': """
E|-----0-------0-------0-------|
B|---1---1---1---1---1---1-----|
G|-0-------0-------0-----------|
D|-----------------------------|
A|-------3-------3-------3-----|
E|-3-----------------------3---|
  T 1 2 3 T 1 2 3 T 1 2 3 T 1
(C chord example - alternating bass)

Bass notes for common chords:
C: 5th string (A) and 4th string (D)
G: 6th string (E) and 5th string (A)
D: 4th string (D) and 5th string (A)
A: 5th string (A) and 4th string (D)
E: 6th string (E) and 5th string (A)
""",
                'practice_steps': [
                    '1. Master thumb alternating bass (10 min daily)',
                    '2. Add index finger only (thumb + 1)',
                    '3. Add middle finger (thumb + 1 + 2)',
                    '4. Add ring finger for complete pattern',
                    '5. Practice at 40% tempo, increase gradually',
                    '6. Practice chord changes with pattern',
                    '7. Play along with slow songs'
                ],
                'common_mistakes': [
                    '❌ Fingers interfering with thumb rhythm',
                    '❌ Rushing the pattern',
                    '❌ Not letting notes ring together',
                    '❌ Inconsistent thumb alternation',
                    '❌ Trying to learn too fast'
                ]
            }
    
    def _generate_tab_example(self, pattern_type):
        """Generate tablature example for fingerpicking"""
        if pattern_type == 'waltz':
            return """
E|-----0-------0-------|
B|---1---1---1---1-----|
G|-0-------0-----------|
D|---------------------|
A|---------------------|
E|-0-------------------|
  1   2   3   1   2   3
  T   1   2   3   2   1
(C chord - 3/4 time)
"""
        else:
            return """
E|-----0-------0-------|
B|---1---1---1---1-----|
G|-0-------0-----------|
D|---------------------|
A|-------3-------------|
E|-3-------------------|
  T 1 2 3 T 1 2 3
(C chord - Travis picking)
"""
    
    def generate_practice_routine(self, chords, tempo, pattern):
        """Generate comprehensive practice routine with detailed steps"""
        routine = {
            'steps': [
                {
                    'step': 1,
                    'title': 'Warm Up & Stretch (Essential)',
                    'description': 'Prepare your hands and prevent repetitive strain injury',
                    'duration': '5-7 minutes',
                    'exercises': [
                        'Gently stretch each finger back (hold 10 seconds each)',
                        'Make fists and release slowly (repeat 10 times)',
                        'Rotate wrists clockwise and counter-clockwise (10 each direction)',
                        'Shake hands loosely to release tension',
                        'Play chromatic scale slowly up and down the neck',
                        'Light strumming on open strings to wake up muscles',
                        'Finger independence: lift one finger at a time while others stay down'
                    ],
                    'why_important': 'Prevents injury and improves flexibility'
                },
                {
                    'step': 2,
                    'title': 'Learn Individual Chord Shapes',
                    'description': f"Master these {len(chords)} chords one at a time with perfect form",
                    'duration': '10-15 minutes',
                    'exercises': [
                'Practice each chord shape for 1-2 minutes',
                        'Play each string individually - ensure all strings ring clearly',
                        'Memorize finger positions without looking at fretboard',
                        'Practice forming each chord from relaxed hand position',
                        'Use proper finger placement: on fingertips, fingers curved',
                        'Check thumb position: behind neck, not gripping too hard',
                        'Strum each chord 4 times, then switch to next chord'
                    ],
                    'why_important': 'Foundation for everything - must be solid',
                    'quality_checklist': [
                        '✓ All strings ring clearly',
                        '✓ Fingers on tips, not flat',
                        '✓ No buzzing or muted strings',
                        '✓ Thumb relaxed behind neck'
                    ]
                },
                {
                    'step': 3,
                    'title': 'Chord Transition Practice',
                    'description': 'Smooth, quick transitions between consecutive chords',
                    'duration': '15 minutes',
                    'exercises': [
                        'Practice each consecutive chord pair for 2 minutes',
                        'Find "pivot fingers" (fingers that stay in same position)',
                        'Move all fingers simultaneously, not one at a time',
                        'Start slowly: 4 beats per chord, then 2 beats, then 1 beat',
                        'Use metronome starting at 60 BPM',
                        'Visualize next chord shape while playing current chord',
                        'Practice "in the air" - form chord shapes without guitar'
                    ],
                    'why_important': 'Smooth transitions = professional sound',
                    'common_mistakes': [
                        '❌ Looking at fretting hand (trust your muscle memory)',
                        '❌ Moving fingers one at a time (move together)',
                        '❌ Gripping too hard (stay relaxed)',
                        '❌ Stopping the rhythm during changes'
                    ]
                },
                {
                    'step': 4,
                    'title': 'Strumming Pattern Isolation',
                    'description': f"Master the {pattern['name']} pattern: {pattern['pattern']}",
                    'duration': '10-15 minutes',
                    'exercises': [
                        'Practice pattern on single easy chord (C or G major)',
                        'Say pattern out loud while playing: "Down-Down-Up-Up-Down-Up"',
                        'Practice with muted strings first (focus purely on rhythm)',
                        'Use metronome at 50% of target tempo',
                        'Watch your strumming hand - ensure consistent motion',
                        'Record yourself - listen for timing inconsistencies',
                        'Practice until you can do it without thinking'
                    ],
                    'why_important': 'Rhythm must be automatic before combining with chords',
                    'metronome_progression': [
                        f'Start: {int(tempo * 0.5)} BPM',
                        f'After 5 min: {int(tempo * 0.6)} BPM',
                        f'After 10 min: {int(tempo * 0.7)} BPM',
                        f'Target: {int(tempo)} BPM'
                    ]
                },
                {
                    'step': 5,
                    'title': 'Combine Chords & Strumming (Slow Practice)',
                    'description': 'Put it all together at reduced speed - most important step!',
                    'duration': '15-20 minutes',
                    'exercises': [
                        f"Set metronome to {int(tempo * 0.5)} BPM (50% speed)",
                        'Play through entire chord progression with strumming',
                        'Stop and restart if you make mistakes (don\'t practice errors)',
                        'Focus on smooth chord changes between strums',
                        'Maintain relaxed hand and arm position throughout',
                        'Count out loud to stay on rhythm',
                        'If struggling, slow down even more'
                    ],
                    'why_important': 'Slow practice = fast progress. Speed comes naturally.',
                    'golden_rule': '⭐ If you can\'t play it slowly, you can\'t play it fast!'
                },
                {
                    'step': 6,
                    'title': 'Gradual Speed Building',
                    'description': f"Build up to target tempo: {int(tempo)} BPM",
                    'duration': '15-20 minutes',
                    'exercises': [
                        f"Start at {int(tempo * 0.6)} BPM (60% speed)",
                        'Increase by 5 BPM every 3 minutes',
                        'If you struggle at any speed, drop back 10 BPM',
                        'Accuracy is MORE important than speed - always!',
                        'Record yourself at each tempo increase',
                        'Take 30-second breaks between tempo increases',
                        'Never sacrifice accuracy for speed'
                    ],
                    'why_important': 'Gradual building prevents bad habits and injury',
                    'tempo_progression': [
                        f'{int(tempo * 0.6)} BPM - 3 minutes',
                        f'{int(tempo * 0.7)} BPM - 3 minutes',
                        f'{int(tempo * 0.8)} BPM - 3 minutes',
                        f'{int(tempo * 0.9)} BPM - 3 minutes',
                        f'{int(tempo)} BPM - remaining time'
                    ]
                },
                {
                    'step': 7,
                    'title': 'Play Along with Original Recording',
                    'description': 'Match the actual song - train your ear',
                    'duration': '10-15 minutes',
                    'exercises': [
                        'Start by just following chord changes (no strumming)',
                        'Add strumming pattern once comfortable with changes',
                        'Listen for timing cues and fills in the original',
                        'Try to match the energy and dynamics of recording',
                        'Don\'t worry about perfection - focus on feel',
                        'Use loop feature to practice difficult sections',
                        'Play along at 75% speed using playback software'
                    ],
                    'why_important': 'Develops timing and musicality',
                    'apps_recommended': ['YouTube (speed control)', 'Audacity', 'Amazing Slow Downer']
                },
                {
                    'step': 8,
                    'title': 'Performance Practice (No Stopping!)',
                    'description': 'Play through entire song without stopping - simulate performance',
                    'duration': '10-15 minutes',
                    'exercises': [
                        'Play the full song 3 times without stopping',
                        'Keep going even if you make mistakes (recovery is a skill)',
                        'Focus on recovery, not perfection',
                        'Record your final attempt for honest self-assessment',
                        'Note what sections need more isolated practice',
                        'Imagine performing for an audience',
                        'Celebrate what went right, note what needs work'
                    ],
                    'why_important': 'Builds confidence and identifies weak spots',
                    'reflection_questions': [
                        'Which chord changes were smooth?',
                        'Where did I struggle?',
                        'Was my rhythm consistent?',
                        'What needs more practice tomorrow?'
                    ]
                }
            ],
            'total_time': '90-120 minutes',
            'tips': [
                '🎯 Use a metronome - it\'s the #1 tool for improvement',
                '🎸 Keep guitar properly tuned - check before EVERY practice session',
                '💪 Take 5-minute breaks every 30 minutes to avoid hand fatigue',
                '📹 Record yourself weekly - video reveals what you can\'t feel',
                '🎵 Practice problem sections in isolation - drill weak spots',
                '⏰ Consistency beats length - 20 minutes daily > 3 hours weekly',
                '👂 Train your ear - listen to the song 10+ times before practicing',
                '📝 Keep a practice journal - track progress and problem areas',
                '😌 Stay relaxed - tension = mistakes and potential injury',
                '🎉 Celebrate small wins - progress is incremental, not overnight',
                '🔄 Always warm up and cool down every session',
                '🎼 Slow practice is smart practice - speed comes naturally',
                '💡 Quality over quantity - 20 focused minutes > 2 unfocused hours',
                '🎭 Practice like you\'ll perform - build good habits now',
                '🔊 Practice at different volumes - dynamics matter',
                '📱 Turn off distractions - phone away, full focus'
            ],
            'weekly_plan': {
                'day_1_2': 'Focus on chord shapes and muscle memory (Steps 1-3). Goal: Perfect chord clarity.',
                'day_3_4': 'Master strumming pattern independently (Steps 1, 4). Goal: Automatic rhythm.',
                'day_5_6': 'Combine chords with strumming at slow tempo (Steps 1-6). Goal: Smooth integration.',
                'day_7': 'Full song playthrough, play along with original (Steps 1, 7-8). Goal: Musical performance.'
            },
            'common_mistakes': [
                '❌ Rushing through difficult parts - ALWAYS SLOW DOWN',
                '❌ Practicing mistakes repeatedly - stop and correct immediately',
                '❌ Gripping neck too hard - keep thumb and fingers relaxed',
                '❌ Looking at right hand while strumming - trust your rhythm',
                '❌ Not using metronome - timing suffers without external reference',
                '❌ Practicing only at full speed - build up gradually always',
                '❌ Ignoring proper posture - affects playability and causes strain',
                '❌ Not taking breaks - leads to injury and diminished returns',
                '❌ Practicing too long - quality drops after fatigue sets in',
                '❌ Comparing yourself to others - focus on YOUR progress'
            ],
            'troubleshooting': {
                'chord_buzzing': [
                    'Press harder (but not too hard)',
                    'Move finger closer to fret wire',
                    'Check if fingers are on tips (curved)',
                    'Ensure thumb is behind neck for leverage'
                ],
                'cant_switch_fast': [
                    'Practice transitions in isolation',
                    'Find pivot/anchor fingers',
                    'Visualize next chord before switching',
                    'Slow down even more - speed comes later'
                ],
                'timing_problems': [
                    'Always use metronome',
                    'Count out loud: 1-and-2-and-3-and-4-and',
                    'Tap foot on downbeats',
                    'Record yourself to hear issues'
                ],
                'hand_pain': [
                    'Stop immediately - don\'t practice through pain',
                    'Check if gripping too hard',
                    'Take more frequent breaks',
                    'Ensure proper posture and hand position',
                    'If pain persists, see a doctor'
                ]
            },
            'motivation_tips': [
                '🌟 Set small, achievable daily goals',
                '📈 Track your progress in a journal',
                '🎥 Record yourself monthly - see how far you\'ve come',
                '🎵 Learn songs you love - stay motivated',
                '👥 Play with others when possible - builds confidence',
                '🏆 Reward yourself for milestones reached',
                '⏳ Remember: Every pro was once a beginner',
                '💭 Focus on the journey, not just the destination'
            ]
        }
        
        return routine