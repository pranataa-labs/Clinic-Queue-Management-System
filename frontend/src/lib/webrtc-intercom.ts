// WebRTC Intercom Manager between Doctor Console and Display Speakers
import { apiClient } from './api-client';

const ICE_SERVERS: RTCConfiguration = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
  ],
};

export interface IntercomOfferMetadata {
  doctor_name?: string;
  room_name?: string;
  clinic_name?: string;
}

export class WebRtcIntercom {
  private peer: RTCPeerConnection | null = null;
  private localStream: MediaStream | null = null;
  private audioElement: HTMLAudioElement | null = null;
  private channelId: string = 'clinic_intercom_main';
  private pollingInterval: NodeJS.Timeout | null = null;

  // --- OPERATOR / DOCTOR MIC SENDER ---
  public async startBroadcasting(
    metadata?: IntercomOfferMetadata,
    onStatusChange?: (status: string) => void
  ): Promise<void> {
    try {
      if (onStatusChange) onStatusChange('Mengaktifkan Mikrofon...');
      this.localStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      this.peer = new RTCPeerConnection(ICE_SERVERS);

      this.localStream.getTracks().forEach((track) => {
        if (this.peer && this.localStream) {
          this.peer.addTrack(track, this.localStream);
        }
      });

      this.peer.onicecandidate = async (event) => {
        if (event.candidate) {
          await apiClient.sendIceCandidate(this.channelId, 'operator', event.candidate);
        }
      };

      const offer = await this.peer.createOffer();
      await this.peer.setLocalDescription(offer);

      await apiClient.sendOffer(this.channelId, offer, metadata);
      if (onStatusChange) onStatusChange('Menunggu Sambungan Display TV...');

      // Poll for answer
      let attempts = 0;
      this.pollingInterval = setInterval(async () => {
        attempts++;
        if (attempts > 30) {
          this.stopBroadcasting();
          if (onStatusChange) onStatusChange('Koneksi timeout');
          return;
        }

        const answer = await apiClient.getAnswer(this.channelId);
        if (answer && this.peer && this.peer.signalingState !== 'stable') {
          await this.peer.setRemoteDescription(new RTCSessionDescription(answer));

          // Fetch display ICE candidates
          const candidates = await apiClient.getIceCandidates(this.channelId, 'display');
          for (const cand of candidates) {
            try {
              await this.peer.addIceCandidate(new RTCIceCandidate(cand));
            } catch {
              // ignore duplicate candidate
            }
          }

          if (this.pollingInterval) clearInterval(this.pollingInterval);
          if (onStatusChange) onStatusChange('Intercom Aktif (Live Suara)');
        }
      }, 1000);
    } catch (err) {
      console.error('Failed to start WebRTC broadcast:', err);
      if (onStatusChange) onStatusChange('Gagal membuka mikrofon');
      throw err;
    }
  }

  public stopBroadcasting(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
      this.localStream = null;
    }
    if (this.peer) {
      this.peer.close();
      this.peer = null;
    }
    apiClient.resetWebRtc(this.channelId).catch(() => {});
  }

  // --- DISPLAY RECEIVER ---
  public startListening(
    onIncomingStream?: (isActive: boolean, metadata?: IntercomOfferMetadata) => void
  ): void {
    if (this.pollingInterval) clearInterval(this.pollingInterval);

    this.pollingInterval = setInterval(async () => {
      // Check if an offer exists and we are not connected
      if (!this.peer || this.peer.connectionState === 'closed' || this.peer.connectionState === 'failed') {
        const offer = await apiClient.getOffer(this.channelId);
        if (offer && offer.type === 'offer') {
          await this.handleIncomingOffer(offer, onIncomingStream);
        } else {
          // If no offer in cache, ensure state is reported as inactive
          if (onIncomingStream && !this.peer) {
            onIncomingStream(false);
          }
        }
      } else {
        // Peer is connected, verify offer still exists
        const offer = await apiClient.getOffer(this.channelId);
        if (!offer) {
          this.stopListening();
          if (onIncomingStream) onIncomingStream(false);
        }
      }
    }, 2000);
  }

  private async handleIncomingOffer(
    offer: any,
    onIncomingStream?: (isActive: boolean, metadata?: IntercomOfferMetadata) => void
  ): Promise<void> {
    try {
      this.peer = new RTCPeerConnection(ICE_SERVERS);

      const metadata: IntercomOfferMetadata = {
        doctor_name: offer.doctor_name,
        room_name: offer.room_name,
        clinic_name: offer.clinic_name,
      };

      this.peer.ontrack = (event) => {
        if (!this.audioElement) {
          this.audioElement = new Audio();
          this.audioElement.autoplay = true;
        }
        this.audioElement.srcObject = event.streams[0];
        this.audioElement.play().catch((e) => console.warn('Display audio autoplay blocked:', e));
        if (onIncomingStream) onIncomingStream(true, metadata);
      };

      this.peer.onconnectionstatechange = () => {
        if (this.peer?.connectionState === 'disconnected' || this.peer?.connectionState === 'closed') {
          if (onIncomingStream) onIncomingStream(false);
        }
      };

      this.peer.onicecandidate = async (event) => {
        if (event.candidate) {
          await apiClient.sendIceCandidate(this.channelId, 'display', event.candidate);
        }
      };

      await this.peer.setRemoteDescription(new RTCSessionDescription(offer));
      const answer = await this.peer.createAnswer();
      await this.peer.setLocalDescription(answer);

      await apiClient.sendAnswer(this.channelId, answer);

      // Fetch operator ICE candidates
      const candidates = await apiClient.getIceCandidates(this.channelId, 'operator');
      for (const cand of candidates) {
        try {
          await this.peer.addIceCandidate(new RTCIceCandidate(cand));
        } catch {
          // ignore duplicate
        }
      }
    } catch (err) {
      console.warn('Error handling incoming WebRTC offer:', err);
      if (onIncomingStream) onIncomingStream(false);
    }
  }

  public stopListening(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
    if (this.audioElement) {
      this.audioElement.pause();
      this.audioElement.srcObject = null;
    }
    if (this.peer) {
      this.peer.close();
      this.peer = null;
    }
  }
}
