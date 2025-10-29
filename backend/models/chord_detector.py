import numpy as np
import librosa
from scipy.ndimage import median_filter
from scipy.signal import find_peaks
from utils.music_theory import MusicTheory

class ChordDetector:
    """Enhanced chord detector with ultra-accurate plucking detection"""
    
    def __init__(self, confidence_threshold=0.6):
        self.confidence_threshold = confidence_threshold
        self.music_theory = MusicTheory()
        
    def detect_chords_and_patterns(self, chromagram, beat_times, sr, hop_length, y, y_harmonic):
        """
        Detect chords, plucking patterns, and solo sections with high accuracy
        """
        print("\n=== CHORD & PATTERN DETECTION ===")
        
        # Normalize chromagram
        chromagram = librosa.util.normalize(chromagram, axis=0)
        chromagram_smooth = median_filter(chromagram, size=(1, 5))
        
        # Convert beat times to frame indices
        beat_frames = librosa.time_to_frames(beat_times, sr=sr, hop_length=hop_length)
        
        segments = []
        
        # Analyze each segment between beats
        for i in range(len(beat_frames) - 1):
            start_frame = beat_frames[i]
            end_frame = beat_frames[i + 1]
            start_time = beat_times[i]
            end_time = beat_times[i + 1] if i + 1 < len(beat_frames) else start_time + 1
            
            print(f"\nSegment {i+1}: {start_time:.1f}s - {end_time:.1f}s")
            
            # Extract audio segment
            start_sample = librosa.frames_to_samples(start_frame, hop_length=hop_length)
            end_sample = librosa.frames_to_samples(end_frame, hop_length=hop_length)
            audio_segment_harmonic = y_harmonic[start_sample:end_sample]
            audio_segment_full = y[start_sample:end_sample]
            
            # Check if this is a solo/lead section
            is_solo, solo_confidence = self._detect_solo_section(
                audio_segment_harmonic,
                chromagram_smooth[:, start_frame:end_frame],
                sr
            )
            
            # Detect if this is plucking or strumming with enhanced accuracy
            is_plucking, plucking_confidence, plucking_details = self._detect_plucking_enhanced(
                audio_segment_harmonic,
                audio_segment_full,
                chromagram_smooth[:, start_frame:end_frame],
                sr
            )
            
            # Average chromagram over beat duration
            chroma_segment = np.mean(chromagram_smooth[:, start_frame:end_frame], axis=1)
            
            # Detect chord
            chord, chord_confidence = self._match_chord(chroma_segment)
            
            if is_solo and solo_confidence > 0.7:
                # This is a solo/lead section
                print(f"  → SOLO DETECTED (confidence: {solo_confidence:.2f})")
                segments.append({
                    'type': 'solo',
                    'start_time': float(start_time),
                    'end_time': float(end_time),
                    'duration': float(end_time - start_time),
                    'confidence': float(solo_confidence),
                    'underlying_chord': chord if chord_confidence >= 0.5 else None
                })
            elif is_plucking and plucking_confidence > 0.55:
                # This is a plucking/fingerpicking section
                print(f"  → PLUCKING DETECTED (confidence: {plucking_confidence:.2f})")
                plucking_pattern = self._analyze_plucking_pattern_enhanced(
                    audio_segment_harmonic,
                    audio_segment_full,
                    chroma_segment,
                    plucking_details,
                    sr
                )
                
                segments.append({
                    'type': 'plucking',
                    'chord': chord if chord_confidence >= self.confidence_threshold else None,
                    'pattern': plucking_pattern,
                    'start_time': float(start_time),
                    'end_time': float(end_time),
                    'duration': float(end_time - start_time),
                    'confidence': float(plucking_confidence)
                })
            elif chord_confidence >= self.confidence_threshold:
                # This is a strumming section with clear chord
                print(f"  → CHORD: {chord} (confidence: {chord_confidence:.2f})")
                segments.append({
                    'type': 'chord',
                    'chord': chord,
                    'start_time': float(start_time),
                    'end_time': float(end_time),
                    'duration': float(end_time - start_time),
                    'confidence': float(chord_confidence)
                })
            else:
                # Unclear section or transition
                print(f"  → TRANSITION (unclear)")
                segments.append({
                    'type': 'transition',
                    'start_time': float(start_time),
                    'end_time': float(end_time),
                    'duration': float(end_time - start_time)
                })
        
        # Post-process segments
        segments = self._merge_similar_segments(segments)
        
        print(f"\n=== DETECTION SUMMARY ===")
        chord_count = len([s for s in segments if s['type'] == 'chord'])
        pluck_count = len([s for s in segments if s['type'] == 'plucking'])
        solo_count = len([s for s in segments if s['type'] == 'solo'])
        print(f"Chord sections: {chord_count}")
        print(f"Plucking sections: {pluck_count}")
        print(f"Solo sections: {solo_count}")
        
        return segments
    
    def _detect_plucking_enhanced(self, audio_segment_harmonic, audio_segment_full, chroma_segment, sr):
        """
        ULTRA-SENSITIVE plucking detection - catches even subtle fingerpicking
        """
        if len(audio_segment_harmonic) < sr * 0.05:
            return False, 0.0, {}
        
        details = {}
        
        print(f"  [Plucking Analysis]")
        
        # 1. SUPER SENSITIVE ONSET DETECTION
        onset_env_harmonic = librosa.onset.onset_strength(
            y=audio_segment_harmonic, 
            sr=sr,
            aggregate=np.median
        )
        
        # Multiple onset detection strategies
        onset_frames_sensitive = librosa.onset.onset_detect(
            onset_envelope=onset_env_harmonic,
            sr=sr,
            backtrack=True,
            pre_max=2,
            post_max=2,
            pre_avg=2,
            post_avg=2,
            delta=0.04,   # Low threshold for sensitivity
            wait=8
        )
        
        # Spectral flux onsets
        try:
            spec_flux = librosa.onset.onset_strength(
                y=audio_segment_harmonic,
                sr=sr,
                feature=librosa.feature.spectral_centroid
            )
            
            onset_frames_spectral = librosa.onset.onset_detect(
                onset_envelope=spec_flux,
                sr=sr,
                delta=0.03
            )
        except:
            onset_frames_spectral = np.array([])
        
        # Combine both methods
        all_onsets = np.unique(np.concatenate([onset_frames_sensitive, onset_frames_spectral]))
        onset_density = len(all_onsets) / (len(audio_segment_harmonic) / sr)
        details['onset_density'] = float(onset_density)
        
        print(f"    Onset density: {onset_density:.2f} notes/sec ({len(all_onsets)} onsets)")
        
        # 2. INTER-ONSET INTERVAL (IOI)
        if len(all_onsets) > 1:
            onset_times = librosa.frames_to_time(all_onsets, sr=sr)
            ioi = np.diff(onset_times)
            ioi_mean = np.mean(ioi)
            ioi_std = np.std(ioi)
            ioi_cv = ioi_std / ioi_mean if ioi_mean > 0 else 1.0
            
            details['ioi_mean'] = float(ioi_mean)
            details['ioi_cv'] = float(ioi_cv)
            details['ioi_std'] = float(ioi_std)
            
            print(f"    IOI: mean={ioi_mean:.3f}s, CV={ioi_cv:.2f}")
        else:
            details['ioi_mean'] = 1.0
            details['ioi_cv'] = 1.0
            details['ioi_std'] = 0.0
        
        # 3. POLYPHONY ANALYSIS (KEY INDICATOR)
        chroma_active = np.sum(chroma_segment > 0.25, axis=0)
        polyphony_mean = np.mean(chroma_active)
        polyphony_std = np.std(chroma_active)
        polyphony_max = np.max(chroma_active)
        
        details['polyphony_mean'] = float(polyphony_mean)
        details['polyphony_std'] = float(polyphony_std)
        details['polyphony_max'] = float(polyphony_max)
        
        print(f"    Polyphony: mean={polyphony_mean:.1f}, max={polyphony_max}")
        
        # 4. SPECTRAL CHARACTERISTICS
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_segment_harmonic, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_segment_harmonic, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_segment_harmonic, sr=sr)
        
        try:
            spectral_flatness = librosa.feature.spectral_flatness(y=audio_segment_harmonic)
        except:
            spectral_flatness = np.array([[0.5]])
        
        centroid_mean = np.mean(spectral_centroid)
        centroid_std = np.std(spectral_centroid)
        bandwidth_mean = np.mean(spectral_bandwidth)
        flatness_mean = np.mean(spectral_flatness)
        
        details['centroid_mean'] = float(centroid_mean)
        details['centroid_std'] = float(centroid_std)
        details['bandwidth_mean'] = float(bandwidth_mean)
        details['flatness_mean'] = float(flatness_mean)
        
        # 5. TEMPORAL ENVELOPE
        rms = librosa.feature.rms(y=audio_segment_harmonic)[0]
        
        # Find peaks with lower threshold
        rms_peaks, peak_properties = find_peaks(
            rms, 
            height=np.mean(rms) * 0.3,
            distance=3
        )
        rms_peak_density = len(rms_peaks) / (len(audio_segment_harmonic) / sr)
        
        details['rms_peak_density'] = float(rms_peak_density)
        details['rms_peaks_count'] = int(len(rms_peaks))
        
        print(f"    RMS peaks: {len(rms_peaks)}, density={rms_peak_density:.2f}/sec")
        
        # 6. ZERO CROSSING RATE
        zcr = librosa.feature.zero_crossing_rate(audio_segment_harmonic)[0]
        zcr_mean = np.mean(zcr)
        zcr_std = np.std(zcr)
        
        details['zcr_mean'] = float(zcr_mean)
        details['zcr_std'] = float(zcr_std)
        
        # 7. SPECTRAL FLUX
        spectral_flux = np.mean(np.abs(np.diff(chroma_segment, axis=1)))
        details['spectral_flux'] = float(spectral_flux)
        
        print(f"    Spectral flux: {spectral_flux:.3f}")
        
        # 8. ATTACK CHARACTERISTICS
        attack_times = []
        if len(all_onsets) > 0:
            for onset_idx in all_onsets[:15]:
                if onset_idx < len(rms) - 15:
                    post_onset_rms = rms[onset_idx:onset_idx+15]
                    if len(post_onset_rms) > 0:
                        peak_idx = np.argmax(post_onset_rms)
                        attack_time = peak_idx * (len(audio_segment_harmonic) / sr / len(rms))
                        attack_times.append(attack_time)
        
        avg_attack_time = np.mean(attack_times) if len(attack_times) > 0 else 0.1
        details['avg_attack_time'] = float(avg_attack_time)
        details['attack_count'] = int(len(attack_times))
        
        # 9. PITCH CONTINUITY
        try:
            pitches, magnitudes = librosa.piptrack(
                y=audio_segment_harmonic, 
                sr=sr, 
                fmin=80, 
                fmax=1000
            )
            pitch_continuity = np.sum(magnitudes > np.median(magnitudes) * 0.5) / magnitudes.size
        except:
            pitch_continuity = 0.3
        
        details['pitch_continuity'] = float(pitch_continuity)
        
        print(f"    Pitch continuity: {pitch_continuity:.3f}")
        
        # === ENHANCED SCORING SYSTEM ===
        plucking_score = 0.0
        confidence_factors = []
        
        print(f"    [Scoring]")
        
        # CRITERION 1: Onset Density (25% weight)
        if 1.5 <= onset_density <= 12.0:
            if 2.5 <= onset_density <= 7.0:
                onset_score = 1.0
            else:
                onset_score = 0.8
            plucking_score += onset_score * 0.25
            confidence_factors.append(('onset_density', onset_score * 0.25))
            print(f"      ✓ Onset density matches: +{onset_score * 0.25:.3f}")
        elif onset_density > 0.8:
            onset_score = 0.4
            plucking_score += onset_score * 0.25
            confidence_factors.append(('onset_density_low', onset_score * 0.25))
            print(f"      ~ Onset density (low): +{onset_score * 0.25:.3f}")
        
        # CRITERION 2: Low Polyphony (20% weight) - KEY
        if polyphony_mean < 3.5:
            poly_score = (3.5 - polyphony_mean) / 3.5
            plucking_score += poly_score * 0.20
            confidence_factors.append(('low_polyphony', poly_score * 0.20))
            print(f"      ✓ Low polyphony: +{poly_score * 0.20:.3f}")
        
        # CRITERION 3: Regular IOI (15% weight)
        if details['ioi_cv'] < 0.6 and details['ioi_mean'] > 0.05:
            ioi_score = 1.0 - min(details['ioi_cv'], 1.0)
            plucking_score += ioi_score * 0.15
            confidence_factors.append(('regular_ioi', ioi_score * 0.15))
            print(f"      ✓ Regular timing: +{ioi_score * 0.15:.3f}")
        
        # CRITERION 4: Spectral Flux (10% weight)
        if spectral_flux > 0.08:
            flux_score = min(spectral_flux / 0.25, 1.0)
            plucking_score += flux_score * 0.10
            confidence_factors.append(('spectral_flux', flux_score * 0.10))
            print(f"      ✓ High spectral variation: +{flux_score * 0.10:.3f}")
        
        # CRITERION 5: RMS Peaks (10% weight)
        if 1.5 <= rms_peak_density <= 12.0:
            rms_score = 1.0 - abs(rms_peak_density - 5.0) / 7.0
            plucking_score += rms_score * 0.10
            confidence_factors.append(('rms_peaks', rms_score * 0.10))
            print(f"      ✓ RMS peak pattern: +{rms_score * 0.10:.3f}")
        
        # CRITERION 6: Fast Attack (10% weight)
        if 0 < avg_attack_time < 0.08:
            attack_score = 1.0 - (avg_attack_time / 0.08)
            plucking_score += attack_score * 0.10
            confidence_factors.append(('fast_attack', attack_score * 0.10))
            print(f"      ✓ Fast attack times: +{attack_score * 0.10:.3f}")
        
        # CRITERION 7: Spectral Characteristics (5% weight)
        if centroid_std > 200:
            spec_score = min(centroid_std / 800, 1.0)
            plucking_score += spec_score * 0.05
            confidence_factors.append(('spectral_variation', spec_score * 0.05))
            print(f"      ✓ Spectral variation: +{spec_score * 0.05:.3f}")
        
        # CRITERION 8: Low Pitch Continuity (5% weight)
        if pitch_continuity < 0.4:
            continuity_score = 1.0 - pitch_continuity
            plucking_score += continuity_score * 0.05
            confidence_factors.append(('low_continuity', continuity_score * 0.05))
            print(f"      ✓ Low sustain: +{continuity_score * 0.05:.3f}")
        
        # BONUS CRITERIA
        if len(all_onsets) >= 3 and polyphony_mean < 2.5:
            plucking_score += 0.15
            confidence_factors.append(('discrete_notes_bonus', 0.15))
            print(f"      ★ BONUS - Discrete notes: +0.15")
        
        if spectral_flux > 0.15:
            plucking_score += 0.10
            confidence_factors.append(('high_flux_bonus', 0.10))
            print(f"      ★ BONUS - Very high variation: +0.10")
        
        details['confidence_factors'] = confidence_factors
        details['score_breakdown'] = {factor: score for factor, score in confidence_factors}
        
        print(f"    FINAL PLUCKING SCORE: {plucking_score:.3f}")
        
        # THRESHOLD: 0.55 (lowered for better detection)
        is_plucking = plucking_score > 0.55
        
        if is_plucking:
            print(f"    ✓✓✓ PLUCKING DETECTED! ✓✓✓")
        else:
            print(f"    ✗ Not plucking (threshold: 0.55)")
        
        return is_plucking, plucking_score, details
    
    def _analyze_plucking_pattern_enhanced(self, audio_segment, audio_segment_full, chroma_segment, details, sr):
        """
        Ultra-detailed plucking pattern analysis
        """
        # Combined onset detection
        onset_env = librosa.onset.onset_strength(y=audio_segment, sr=sr)
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            backtrack=True,
            delta=0.04
        )
        
        # Spectral method
        try:
            spec_flux = librosa.onset.onset_strength(
                y=audio_segment,
                sr=sr,
                feature=librosa.feature.spectral_centroid
            )
            onset_frames_spec = librosa.onset.onset_detect(
                onset_envelope=spec_flux,
                sr=sr,
                delta=0.03
            )
        except:
            onset_frames_spec = np.array([])
        
        # Combine
        all_onsets = np.unique(np.concatenate([onset_frames, onset_frames_spec]))
        
        num_notes = len(all_onsets)
        duration = len(audio_segment) / sr
        notes_per_second = num_notes / duration if duration > 0 else 0
        
        print(f"    Pattern: {num_notes} notes in {duration:.1f}s = {notes_per_second:.1f} notes/sec")
        
        # Detect prominent notes
        prominent_notes = []
        for i in range(12):
            note_strength = np.max(chroma_segment[i])
            if note_strength > 0.25:
                note_name = self.music_theory.NOTE_NAMES[i]
                prominent_notes.append({
                    'note': note_name,
                    'strength': float(note_strength)
                })
        
        # Sort by strength
        prominent_notes.sort(key=lambda x: x['strength'], reverse=True)
        note_names = [n['note'] for n in prominent_notes[:8]]
        
        # Detailed pattern classification
        if notes_per_second < 1.0:
            pattern_type = "Very Slow Arpeggio"
            description = "Extremely slow, deliberate note-by-note playing with long pauses between notes"
        elif notes_per_second < 2.0:
            pattern_type = "Slow Arpeggio"
            description = "Slow, sustained note-by-note playing - ballad style fingerpicking"
        elif notes_per_second < 3.5:
            pattern_type = "Moderate Arpeggio"
            description = "Steady arpeggio pattern with clear note separation - classic acoustic style"
        elif notes_per_second < 5.0:
            pattern_type = "Standard Fingerpicking"
            description = "Classic fingerpicking style - steady, rhythmic, and controlled"
        elif notes_per_second < 7.0:
            pattern_type = "Fast Fingerpicking"
            description = "Quick, complex fingerpicking pattern - requires good technique"
        elif notes_per_second < 9.5:
            pattern_type = "Rapid Arpeggio"
            description = "Very fast ascending/descending note sequences - advanced level"
        elif notes_per_second < 12.0:
            pattern_type = "Speed Picking"
            description = "Extremely fast repetitive picking technique"
        else:
            pattern_type = "Tremolo Picking"
            description = "Ultra-fast tremolo or sweep picking - virtuoso level"
        
        # Determine regularity
        ioi_cv = details.get('ioi_cv', 1.0)
        if ioi_cv < 0.3:
            regularity = "Very Regular"
            regularity_desc = "Metronome-like precision - very consistent timing"
        elif ioi_cv < 0.5:
            regularity = "Regular"
            regularity_desc = "Consistent timing with minimal variation"
        elif ioi_cv < 0.7:
            regularity = "Somewhat Regular"
            regularity_desc = "Mostly consistent with some intentional variation"
        else:
            regularity = "Irregular"
            regularity_desc = "Variable timing - rubato or free-style interpretation"
        
        # Generate enhanced notation
        notation = self._generate_plucking_notation_enhanced(
            num_notes,
            duration,
            details.get('ioi_mean', 0.5),
            notes_per_second
        )
        
        # Detect pattern style
        pattern_style = self._detect_plucking_style(
            notes_per_second,
            details.get('polyphony_mean', 2.0),
            ioi_cv
        )
        
        return {
            'type': pattern_type,
            'description': description,
            'notes_per_second': float(notes_per_second),
            'num_notes': int(num_notes),
            'prominent_notes': note_names,
            'notation': notation,
            'regularity': regularity,
            'regularity_description': regularity_desc,
            'pattern_style': pattern_style,
            'confidence_breakdown': details.get('score_breakdown', {}),
            'technical_details': {
                'onset_density': float(details.get('onset_density', 0)),
                'polyphony': float(details.get('polyphony_mean', 0)),
                'spectral_variation': float(details.get('spectral_flux', 0)),
                'ioi_coefficient_variation': float(ioi_cv),
                'attack_speed': float(details.get('avg_attack_time', 0)),
                'pitch_continuity': float(details.get('pitch_continuity', 0))
            }
        }
    
    def _detect_plucking_style(self, notes_per_sec, polyphony, ioi_cv):
        """Detect specific plucking style"""
        if polyphony < 1.5 and ioi_cv < 0.4:
            return "Travis Picking Style (alternating bass)"
        elif polyphony < 2.0 and notes_per_sec > 5:
            return "Classical Arpeggio (fast single notes)"
        elif ioi_cv > 0.6:
            return "Free-form Fingerstyle (rubato)"
        elif notes_per_sec < 2 and polyphony < 2:
            return "Slow Picking/Ballad Style"
        elif notes_per_sec > 7:
            return "Speed Picking/Tremolo"
        else:
            return "Standard Fingerpicking"
    
    def _generate_plucking_notation_enhanced(self, num_notes, duration, ioi_mean, notes_per_sec):
        """Generate detailed tablature notation"""
        if notes_per_sec < 1.0:
            return "T - - - - - - - (whole notes, very sparse - one note per measure)"
        elif notes_per_sec < 1.5:
            return "T - - - 1 - - - (very slow picking - ballad tempo)"
        elif notes_per_sec < 2.5:
            return "T - 1 - 2 - 3 - (slow arpeggio - half note feel)"
        elif notes_per_sec < 3.5:
            return "T 1 - 2 - 3 - (moderate arpeggio - quarter notes)"
        elif notes_per_sec < 5.0:
            return "T 1 2 3 T 1 2 3 (standard fingerpicking - eighth notes)"
        elif notes_per_sec < 7.0:
            return "T1 2 3 T1 2 3 (fast fingerpicking - running eighths)"
        elif notes_per_sec < 9.0:
            return "T123 T123 T123 (rapid arpeggio - sixteenth notes)"
        else:
            return "T1T2T3T1T2T3 (tremolo/speed picking - very fast)"
    
    def _detect_solo_section(self, audio_segment, chroma_segment, sr):
        """Detect guitar solo sections with improved accuracy"""
        if len(audio_segment) < sr * 0.1:
            return False, 0.0
        
        # 1. Pitch detection
        try:
            pitches, magnitudes = librosa.piptrack(y=audio_segment, sr=sr, fmin=80, fmax=1000)
            pitch_density = np.sum(magnitudes > np.median(magnitudes)) / magnitudes.size
        except:
            pitch_density = 0
        
        # 2. Spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_segment, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_segment, sr=sr))
        
        # 3. Melodic contour
        chroma_diff = np.diff(chroma_segment, axis=1)
        melodic_movement = np.mean(np.abs(chroma_diff))
        
        # 4. Monophonic detection
        chroma_peaks_per_frame = np.sum(chroma_segment > 0.5, axis=0)
        avg_simultaneous_notes = np.mean(chroma_peaks_per_frame)
        
        # 5. High frequency energy
        stft = np.abs(librosa.stft(audio_segment))
        high_freq_energy = np.mean(stft[int(len(stft)*0.6):, :])
        low_freq_energy = np.mean(stft[:int(len(stft)*0.4), :])
        freq_ratio = high_freq_energy / (low_freq_energy + 1e-6)
        
        # Scoring
        solo_score = 0.0
        
        if pitch_density > 0.3:
            solo_score += 0.25
        
        if spectral_centroid > 2500:
            solo_score += 0.25
        
        if melodic_movement > 0.15:
            solo_score += 0.20
        
        if avg_simultaneous_notes < 2.0:
            solo_score += 0.15
        
        if freq_ratio > 1.5:
            solo_score += 0.15
        
        is_solo = solo_score > 0.7
        
        return is_solo, float(solo_score)
    
    def _match_chord(self, chroma_vector):
        """Match chroma vector to closest chord with improved accuracy"""
        best_chord = 'N'
        best_confidence = 0.0
        
        # Normalize chroma vector
        chroma_normalized = chroma_vector / (np.sum(chroma_vector) + 1e-6)
        
        for root in self.music_theory.NOTE_NAMES:
            for chord_type in self.music_theory.CHORD_TEMPLATES.keys():
                template = self.music_theory.create_chord_profile(root, chord_type)
                template_normalized = template / (np.sum(template) + 1e-6)
                
                # Use multiple similarity metrics
                correlation = np.corrcoef(chroma_normalized, template_normalized)[0, 1]
                cosine_sim = np.dot(chroma_normalized, template_normalized) / (
                    np.linalg.norm(chroma_normalized) * np.linalg.norm(template_normalized) + 1e-6
                )
                
                # Combined similarity
                similarity = (correlation + cosine_sim) / 2
                
                if similarity > best_confidence:
                    best_confidence = similarity
                    best_chord = self.music_theory.get_chord_name(root, chord_type)
        
        best_confidence = max(0.0, min(1.0, best_confidence))
        
        return best_chord, float(best_confidence)
    
    def _merge_similar_segments(self, segments):
        """Merge consecutive segments of the same type"""
        if len(segments) == 0:
            return []
        
        merged = [segments[0]]
        
        for i in range(1, len(segments)):
            current = segments[i]
            previous = merged[-1]
            
            # Merge same type segments
            if current['type'] == previous['type']:
                if current['type'] == 'chord' and current.get('chord') == previous.get('chord'):
                    previous['end_time'] = current['end_time']
                    previous['duration'] = previous['end_time'] - previous['start_time']
                elif current['type'] in ['plucking', 'solo']:
                    # Merge if very close together (within 0.3 seconds)
                    if current['start_time'] - previous['end_time'] < 0.3:
                        previous['end_time'] = current['end_time']
                        previous['duration'] = previous['end_time'] - previous['start_time']
                        # Update pattern if plucking
                        if current['type'] == 'plucking' and 'pattern' in current:
                            # Merge pattern info
                            if 'pattern' in previous:
                                previous['pattern']['num_notes'] += current['pattern'].get('num_notes', 0)
                    else:
                        merged.append(current)
                else:
                    merged.append(current)
            else:
                merged.append(current)
        
        return merged
    
    def format_segments(self, segments):
        """Format segments for output with separate categories"""
        chord_sections = []
        plucking_sections = []
        solo_sections = []
        
        for segment in segments:
            if segment['type'] == 'chord':
                chord_sections.append(segment)
            elif segment['type'] == 'plucking':
                plucking_sections.append(segment)
            elif segment['type'] == 'solo':
                solo_sections.append(segment)
        
        return {
            'chord_sections': chord_sections,
            'plucking_sections': plucking_sections,
            'solo_sections': solo_sections,
            'all_segments': segments
        }
    
    def get_unique_chords(self, segments):
        """Get unique chords from all segments"""
        unique = []
        seen = set()
        
        for segment in segments:
            chord = None
            if segment['type'] == 'chord':
                chord = segment['chord']
            elif segment['type'] in ['plucking', 'solo'] and segment.get('chord'):
                chord = segment['chord']
            elif segment['type'] in ['plucking', 'solo'] and segment.get('underlying_chord'):
                chord = segment['underlying_chord']
            
            if chord and chord != 'N' and chord not in seen:
                seen.add(chord)
                unique.append(chord)
        
        return unique