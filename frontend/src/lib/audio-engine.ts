// Web Audio & Speech Synthesis Audio Engine for Clinic Queue Calling System

interface AnnouncementTask {
  id: string;
  text: string;
  repeatCount: number;
  chimeType?: 'standard_bell' | 'urgent_chime' | string;
  onStart?: () => void;
  onEnd?: () => void;
}

class AudioEngine {
  private audioCtx: AudioContext | null = null;
  private queue: AnnouncementTask[] = [];
  private isProcessing: boolean = false;
  private isUnlocked: boolean = false;
  private selectedVoice: SpeechSynthesisVoice | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      this.initVoices();
      if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = () => {
          this.initVoices();
        };
      }
    }
  }

  /**
   * Unlock AudioContext and speech synthesis on first user interaction.
   */
  public async unlockAudio(): Promise<boolean> {
    try {
      if (!this.audioCtx) {
        const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        this.audioCtx = new AudioContextClass();
      }

      if (this.audioCtx.state === 'suspended') {
        await this.audioCtx.resume();
      }

      // Warm up SpeechSynthesis
      if ('speechSynthesis' in window) {
        const silentUtterance = new SpeechSynthesisUtterance(' ');
        silentUtterance.volume = 0.01;
        window.speechSynthesis.speak(silentUtterance);
      }

      this.isUnlocked = true;
      return true;
    } catch (e) {
      console.warn('Audio unlock warning:', e);
      return false;
    }
  }

  public getIsUnlocked(): boolean {
    return this.isUnlocked;
  }

  /**
   * Find natural Indonesian voice if available.
   */
  private initVoices(): void {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;

    const voices = window.speechSynthesis.getVoices();
    // Prioritize Indonesian voices: Google Bahasa Indonesia, Microsoft Ardi/Gadis, etc.
    const idVoice = voices.find(v => v.lang.toLowerCase().startsWith('id') || v.lang === 'id-ID' || v.name.toLowerCase().includes('indonesia'));

    if (idVoice) {
      this.selectedVoice = idVoice;
    } else {
      // Fallback to default voice
      this.selectedVoice = voices.find(v => v.default) || voices[0] || null;
    }
  }

  /**
   * Synthesize a two-tone medical chime ("Ting-Tung") using Web Audio API oscillators.
   */
  public playChime(type: 'standard_bell' | 'urgent_chime' | string = 'standard_bell'): Promise<void> {
    return new Promise((resolve) => {
      try {
        if (!this.audioCtx) {
          const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
          this.audioCtx = new AudioContextClass();
        }

        const now = this.audioCtx.currentTime;

        const isUrgent = type === 'urgent_chime';
        const tone1Freq = isUrgent ? 698.46 : 587.33; // F5 or D5
        const tone2Freq = isUrgent ? 880.00 : 880.00; // A5

        // Tone 1
        const osc1 = this.audioCtx.createOscillator();
        const gain1 = this.audioCtx.createGain();
        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(tone1Freq, now);

        gain1.gain.setValueAtTime(0.001, now);
        gain1.gain.exponentialRampToValueAtTime(0.35, now + 0.05);
        gain1.gain.exponentialRampToValueAtTime(0.0001, now + 0.6);

        osc1.connect(gain1);
        gain1.connect(this.audioCtx.destination);
        osc1.start(now);
        osc1.stop(now + 0.6);

        // Tone 2
        const osc2 = this.audioCtx.createOscillator();
        const gain2 = this.audioCtx.createGain();
        osc2.type = 'triangle';
        osc2.frequency.setValueAtTime(tone2Freq, now + 0.35);

        gain2.gain.setValueAtTime(0.001, now + 0.35);
        gain2.gain.exponentialRampToValueAtTime(0.4, now + 0.4);
        gain2.gain.exponentialRampToValueAtTime(0.0001, now + 1.2);

        osc2.connect(gain2);
        gain2.connect(this.audioCtx.destination);
        osc2.start(now + 0.35);
        osc2.stop(now + 1.2);

        setTimeout(() => {
          resolve();
        }, 1100);
      } catch (err) {
        console.warn('Chime generation error:', err);
        resolve();
      }
    });
  }

  /**
   * Enqueue and announce queue calling speech text.
   */
  public enqueueAnnouncement(task: Omit<AnnouncementTask, 'id'>): void {
    const fullTask: AnnouncementTask = {
      ...task,
      id: Math.random().toString(36).substring(7),
    };

    this.queue.push(fullTask);
    this.processQueue();
  }

  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.queue.length === 0) return;

    this.isProcessing = true;
    const current = this.queue.shift();

    if (!current) {
      this.isProcessing = false;
      return;
    }

    try {
      if (current.onStart) current.onStart();

      // 1. Play opening medical chime
      await this.playChime(current.chimeType || 'standard_bell');

      // Small pause before voice begins
      await new Promise(r => setTimeout(r, 250));

      // 2. Play speech synthesis with requested repeats
      const repeats = Math.max(1, current.repeatCount || 1);
      for (let i = 0; i < repeats; i++) {
        await this.speakUtterance(current.text);
        if (i < repeats - 1) {
          // Pause between repeats
          await new Promise(r => setTimeout(r, 800));
        }
      }
    } catch (err) {
      console.error('Announcement playback error:', err);
    } finally {
      if (current.onEnd) current.onEnd();
      this.isProcessing = false;
      // Process next in line if any
      this.processQueue();
    }
  }

  private speakUtterance(text: string): Promise<void> {
    return new Promise((resolve) => {
      if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
        resolve();
        return;
      }

      window.speechSynthesis.cancel(); // Clear any hung speech

      const utterance = new SpeechSynthesisUtterance(text);
      if (this.selectedVoice) {
        utterance.voice = this.selectedVoice;
      }
      utterance.lang = 'id-ID';
      utterance.rate = 0.93; // Slightly measured rate for clear clinic audio
      utterance.pitch = 1.02; // Warm friendly tone
      utterance.volume = 1.0;

      utterance.onend = () => {
        resolve();
      };

      utterance.onerror = (e) => {
        console.warn('Speech synthesis utterance error:', e);
        resolve();
      };

      window.speechSynthesis.speak(utterance);
    });
  }

  public isBusy(): boolean {
    return this.isProcessing || this.queue.length > 0;
  }

  public cancelAll(): void {
    this.queue = [];
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    this.isProcessing = false;
  }
}

export const audioEngine = new AudioEngine();
