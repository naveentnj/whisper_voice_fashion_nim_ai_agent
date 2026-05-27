import React, { useState } from 'react';
import { motion, useScroll } from 'motion/react';
import './index.css';

// Components (We will create these next)
import Header from './components/Header';
import Hero from './components/Hero';
import Categories from './components/Categories';
import Catalog from './components/Catalog';
import VoiceWidget from './components/VoiceWidget';
import CartSidebar from './components/CartSidebar';

function App() {
  const { scrollYProgress } = useScroll();
  const [isCartOpen, setIsCartOpen] = useState(false);
  
  return (
    <>
      {/* Background Orbs */}
      <div className="glow-orb primary" />
      <div className="glow-orb accent" />
      <div className="glow-orb tertiary" />

      {/* Scroll Progress */}
      <motion.div 
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: 'linear-gradient(90deg, var(--primary), var(--accent))',
          transformOrigin: '0%',
          scaleX: scrollYProgress,
          zIndex: 1000,
          boxShadow: '0 0 10px var(--primary-glow)'
        }}
      />

      <Header onOpenCart={() => setIsCartOpen(true)} />
      
      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 2rem' }}>
        <Hero />
        <Categories />
        <Catalog />
      </main>

      <CartSidebar isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
      <VoiceWidget />
      
      <footer style={{
        textAlign: 'center',
        padding: '4rem 2rem',
        borderTop: '1px solid var(--border)',
        marginTop: '6rem'
      }}>
        <p style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.3rem', letterSpacing: '0.2rem', marginBottom: '0.6rem' }}>
          VALENTI <span style={{ fontSize: '0.65rem', fontWeight: 400, color: 'var(--muted)', letterSpacing: '0.1rem', verticalAlign: 'middle' }}>AI COUTURE</span>
        </p>
        <p style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>
          &copy; 2026 Engineered with NVIDIA NIM, CrewAI, Whisper & OmniVoice.
        </p>
      </footer>
    </>
  );
}

export default App;
