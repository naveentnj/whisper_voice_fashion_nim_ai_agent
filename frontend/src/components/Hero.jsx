import React from 'react';
import { motion } from 'motion/react';
import { ArrowDown, Mic, Sparkles } from 'lucide-react';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 40, rotateX: 8 },
  visible: { 
    opacity: 1, 
    y: 0, 
    rotateX: 0,
    transition: { type: "spring", stiffness: 100, damping: 20 }
  }
};

export default function Hero() {
  return (
    <section style={{
      padding: '8rem 4rem 6rem',
      borderRadius: '28px',
      position: 'relative',
      overflow: 'hidden',
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      backdropFilter: 'blur(16px)',
      marginBottom: '2rem',
      marginTop: '2rem'
    }}>
      {/* Top Border Glow Line */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, height: '1px',
        background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent)'
      }} />
      
      {/* Local Parallax Blob */}
      <motion.div 
        animate={{ x: [-15, 15, -15], y: [15, -15, 15] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        style={{
          position: 'absolute',
          top: '-20%',
          right: '-10%',
          width: '500px',
          height: '500px',
          background: 'radial-gradient(circle, rgba(157,78,221,0.08) 0%, transparent 70%)',
          borderRadius: '50%',
          filter: 'blur(60px)'
        }}
      />

      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        style={{ maxWidth: '700px', position: 'relative', zIndex: 2, perspective: '800px' }}
      >
        <motion.p variants={itemVariants} style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.8rem',
          color: 'var(--primary)',
          letterSpacing: '0.1rem',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <Sparkles size={14} /> AI-Powered Fashion Intelligence
        </motion.p>
        
        <motion.h1 variants={itemVariants} style={{
          fontFamily: 'var(--font-display)',
          fontSize: '4rem',
          fontWeight: 800,
          lineHeight: 1.1,
          marginBottom: '1.5rem'
        }}>
          Speak to Your <br /><span className="gradient-text">Wardrobe</span>
        </motion.h1>
        
        <motion.p variants={itemVariants} style={{
          fontSize: '1.05rem',
          color: 'var(--muted)',
          lineHeight: 1.7,
          marginBottom: '2.5rem',
          maxWidth: '550px'
        }}>
          Welcome to a zero-touch shopping experience. Tap the microphone and ask our AI stylist for recommendations, add items to your cart, or check out—all with just your voice.
        </motion.p>
        
        <motion.div variants={itemVariants} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '3rem' }}>
          <motion.button 
            whileHover={{ y: -3, boxShadow: '0 0 30px var(--primary-glow)' }}
            whileTap={{ scale: 0.98 }}
            style={{
              padding: '0.85rem 1.6rem',
              borderRadius: '14px',
              fontWeight: 600,
              fontSize: '0.9rem',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontFamily: 'var(--font-sans)',
              background: 'linear-gradient(135deg, var(--primary) 0%, #7b2cbf 100%)',
              color: '#fff',
              border: 'none'
            }}
            onClick={() => document.getElementById('catalog')?.scrollIntoView({ behavior: 'smooth' })}
          >
            <ArrowDown size={18} /> Explore Collections
          </motion.button>
          
          <motion.button 
            whileHover={{ y: -3, background: 'rgba(255,255,255,0.07)', borderColor: 'var(--text)' }}
            whileTap={{ scale: 0.98 }}
            style={{
              padding: '0.85rem 1.6rem',
              borderRadius: '14px',
              fontWeight: 600,
              fontSize: '0.9rem',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontFamily: 'var(--font-sans)',
              background: 'rgba(255,255,255,0.03)',
              color: 'var(--text)',
              border: '1px solid var(--border)'
            }}
          >
            <Mic size={18} /> Start Voice Chat
          </motion.button>
        </motion.div>
        
        <motion.div variants={itemVariants} style={{ display: 'flex', gap: '3rem' }}>
          {[
            { label: 'Products', val: '50' },
            { label: 'Categories', val: '10' },
            { label: 'AI Agents', val: '3' }
          ].map((stat) => (
            <div key={stat.label} style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{
                fontFamily: 'var(--font-display)',
                fontSize: '2.2rem',
                fontWeight: 800,
                background: 'linear-gradient(135deg, #fff 50%, var(--primary) 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>{stat.val}</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--muted)', letterSpacing: '0.05rem', marginTop: '0.2rem' }}>{stat.label}</span>
            </div>
          ))}
        </motion.div>
      </motion.div>
    </section>
  );
}
