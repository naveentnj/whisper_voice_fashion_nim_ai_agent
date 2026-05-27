import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Sparkles, ChevronDown, Mic } from 'lucide-react';
import axios from 'axios';

export default function VoiceWidget() {
  const [minimized, setMinimized] = useState(false);
  const [status, setStatus] = useState('Idle. Click to speak.');
  const [isRecording, setIsRecording] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    { role: 'bot', text: 'Greetings. I am your personal Valenti style consultant, powered by NVIDIA NIM. How may I customize your wardrobe today?' }
  ]);
  const [asrMode, setAsrMode] = useState('online');
  const [ttsMode, setTtsMode] = useState('online');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const canvasRef = useRef(null);
  const audioRef = useRef(null);

  // Simple waveform animation
  useEffect(() => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.beginPath();
      ctx.moveTo(0, canvas.height / 2);
      
      for (let i = 0; i < canvas.width; i += 5) {
        const amplitude = isRecording ? Math.random() * 20 : Math.random() * 2;
        ctx.lineTo(i, (canvas.height / 2) + (Math.random() > 0.5 ? amplitude : -amplitude));
      }
      
      ctx.strokeStyle = 'rgba(157, 78, 221, 0.8)';
      ctx.lineWidth = 2;
      ctx.stroke();
      animationFrameId = requestAnimationFrame(draw);
    };
    draw();

    return () => cancelAnimationFrame(animationFrameId);
  }, [isRecording]);

  const handleMicClick = async () => {
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
      setStatus('Processing...');
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunksRef.current.push(event.data);
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          await sendAudioToAPI(audioBlob);
          stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        setIsRecording(true);
        setStatus('Listening...');
      } catch (err) {
        console.error('Error accessing mic:', err);
        setStatus('Error accessing microphone.');
      }
    }
  };

  const sendAudioToAPI = async (audioBlob) => {
    const formData = new FormData();
    formData.append('file', audioBlob, 'voice_input.webm');
    formData.append('cart', JSON.stringify([])); // Empty cart for now, could be lifted to context
    formData.append('asr_mode', asrMode);
    formData.append('tts_mode', ttsMode);
    formData.append('session_id', '');
    
    try {
      const response = await axios.post('/api/voice-chat', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const data = response.data;
      
      // Update chat history with both user transcription and bot response
      setChatHistory(prev => [
        ...prev,
        { role: 'user', text: data.transcription },
        { role: 'bot', text: data.response }
      ]);

      if (data.audio_url && audioRef.current) {
        audioRef.current.src = data.audio_url; // Proxied by Vite to Python /static
        audioRef.current.play();
      }
      
      setStatus('Idle. Click to speak.');
    } catch (err) {
      console.error(err);
      setStatus('Error processing voice.');
    }
  };

  return (
    <motion.div 
      initial={false}
      animate={{ height: minimized ? 66 : 480 }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      style={{
        position: 'fixed',
        bottom: '24px',
        right: '24px',
        width: '340px',
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: '22px',
        boxShadow: '0 15px 40px rgba(0,0,0,0.5)',
        zIndex: 500,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        backdropFilter: 'blur(20px)'
      }}
    >
      <div style={{
        padding: '1rem 1.3rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: '1px solid var(--border)',
        background: 'rgba(255,255,255,0.015)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.7rem' }}>
          <Sparkles size={18} color="var(--primary)" style={{ filter: 'drop-shadow(0 0 10px var(--primary-glow))' }} />
          <div>
            <h4 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '0.85rem' }}>VALENTI AI Stylist</h4>
            <p style={{ fontSize: '0.65rem', color: 'var(--muted)' }}>{status}</p>
          </div>
        </div>
        <motion.button 
          onClick={() => setMinimized(!minimized)}
          animate={{ rotate: minimized ? 180 : 0 }}
          style={{ background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer' }}
        >
          <ChevronDown size={20} />
        </motion.button>
      </div>

      <div style={{ padding: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.8rem', flexGrow: 1, overflow: 'hidden' }}>
        <div style={{ flexGrow: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.8rem', paddingRight: '0.3rem', maxHeight: '180px' }}>
          {chatHistory.map((msg, i) => (
            <div key={i} style={{
              maxWidth: '85%',
              padding: '0.6rem 0.9rem',
              borderRadius: '14px',
              fontSize: '0.75rem',
              lineHeight: 1.5,
              alignSelf: msg.role === 'bot' ? 'flex-start' : 'flex-end',
              background: msg.role === 'bot' ? 'rgba(255,255,255,0.03)' : 'var(--primary)',
              color: msg.role === 'bot' ? 'var(--text)' : '#fff',
              border: msg.role === 'bot' ? '1px solid var(--border)' : 'none',
              borderBottomLeftRadius: msg.role === 'bot' ? '4px' : '14px',
              borderBottomRightRadius: msg.role === 'user' ? '4px' : '14px',
              boxShadow: msg.role === 'user' ? '0 4px 12px var(--primary-glow)' : 'none'
            }}>
              {msg.text}
            </div>
          ))}
        </div>

        {/* Engine Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', padding: '0.5rem 0.7rem', background: 'rgba(255,255,255,0.015)', border: '1px solid var(--border)', borderRadius: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.65rem', color: 'var(--muted)', fontWeight: 500 }}>ASR Mode:</span>
            <div style={{ display: 'flex', background: 'rgba(0,0,0,0.35)', padding: '2px', borderRadius: '16px', border: '1px solid var(--border)' }}>
              <button onClick={() => setAsrMode('online')} style={{ border: 'none', background: asrMode === 'online' ? 'var(--primary)' : 'transparent', color: asrMode === 'online' ? '#fff' : 'var(--muted)', fontSize: '0.55rem', fontWeight: 600, padding: '0.15rem 0.45rem', borderRadius: '12px', cursor: 'pointer' }}>Cloud</button>
              <button onClick={() => setAsrMode('offline')} style={{ border: 'none', background: asrMode === 'offline' ? 'var(--primary)' : 'transparent', color: asrMode === 'offline' ? '#fff' : 'var(--muted)', fontSize: '0.55rem', fontWeight: 600, padding: '0.15rem 0.45rem', borderRadius: '12px', cursor: 'pointer' }}>Local GPU</button>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.65rem', color: 'var(--muted)', fontWeight: 500 }}>TTS Mode:</span>
            <div style={{ display: 'flex', background: 'rgba(0,0,0,0.35)', padding: '2px', borderRadius: '16px', border: '1px solid var(--border)' }}>
              <button onClick={() => setTtsMode('online')} style={{ border: 'none', background: ttsMode === 'online' ? 'var(--primary)' : 'transparent', color: ttsMode === 'online' ? '#fff' : 'var(--muted)', fontSize: '0.55rem', fontWeight: 600, padding: '0.15rem 0.45rem', borderRadius: '12px', cursor: 'pointer' }}>Cloud</button>
              <button onClick={() => setTtsMode('offline')} style={{ border: 'none', background: ttsMode === 'offline' ? 'var(--primary)' : 'transparent', color: ttsMode === 'offline' ? '#fff' : 'var(--muted)', fontSize: '0.55rem', fontWeight: 600, padding: '0.15rem 0.45rem', borderRadius: '12px', cursor: 'pointer' }}>Local GPU</button>
            </div>
          </div>
        </div>

        <div style={{ height: '40px', borderRadius: '10px', background: 'rgba(0,0,0,0.2)', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.02)' }}>
          <canvas ref={canvasRef} style={{ width: '100%', height: '100%', display: 'block' }} width={300} height={40} />
        </div>
      </div>

      <div style={{ padding: '1rem 1.3rem', borderTop: '1px solid var(--border)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.6rem', background: 'rgba(0,0,0,0.1)' }}>
        <motion.button 
          onClick={handleMicClick}
          whileHover={{ scale: 1.1, boxShadow: isRecording ? '0 8px 25px var(--accent-glow)' : '0 8px 25px var(--primary-glow)' }}
          whileTap={{ scale: 0.95 }}
          animate={isRecording ? { scale: [1, 1.08, 1], boxShadow: ['0 0 15px var(--accent-glow)', '0 0 25px var(--accent)', '0 0 15px var(--accent-glow)'] } : {}}
          transition={isRecording ? { repeat: Infinity, duration: 1.2 } : {}}
          style={{
            width: '58px', height: '58px', borderRadius: '50%',
            background: isRecording ? 'linear-gradient(135deg, var(--accent) 0%, #d8006b 100%)' : 'linear-gradient(135deg, var(--primary) 0%, #7b2cbf 100%)',
            border: 'none', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
            boxShadow: isRecording ? '0 0 25px var(--accent-glow)' : '0 6px 20px var(--primary-glow)'
          }}
        >
          <Mic size={24} />
        </motion.button>
        <p style={{ fontSize: '0.65rem', color: 'var(--muted)', textAlign: 'center' }}>
          Try: <i>"Show me warm jackets, then add the leather bomber."</i>
        </p>
      </div>

      <audio ref={audioRef} style={{ display: 'none' }} />
    </motion.div>
  );
}
