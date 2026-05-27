import React from 'react';
import { ShoppingBag, Wand2 } from 'lucide-react';
import { motion } from 'motion/react';

export default function Header({ onOpenCart }) {
  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      background: 'rgba(6,6,8,0.65)',
      borderBottom: '1px solid var(--border)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)'
    }}>
      <nav style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', cursor: 'pointer' }}>
          <span style={{
            fontFamily: 'var(--font-display)',
            fontWeight: 800,
            fontSize: '1.5rem',
            letterSpacing: '0.25rem',
            background: 'linear-gradient(135deg, #fff 30%, var(--primary) 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>VALENTI</span>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.6rem',
            fontWeight: 600,
            letterSpacing: '0.08rem',
            padding: '0.2rem 0.55rem',
            borderRadius: '16px',
            background: 'rgba(157,78,221,0.1)',
            border: '1px solid rgba(157,78,221,0.2)',
            color: 'var(--primary)'
          }}>AI COUTURE</span>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.2rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.45rem 0.9rem',
            background: 'rgba(255,255,255,0.02)',
            border: '1px solid var(--border)',
            borderRadius: '24px',
            fontSize: '0.75rem'
          }}>
            <motion.span 
              animate={{ scale: [1, 1.2, 1], opacity: [0.6, 1, 0.6] }}
              transition={{ repeat: Infinity, duration: 2 }}
              style={{
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                background: '#10b981',
                boxShadow: '0 0 8px #10b981'
              }}
            />
            <span style={{ color: 'var(--muted)' }}>Voice Agent Online</span>
          </div>
          
          <motion.button 
            whileHover={{ y: -2, boxShadow: '0 0 15px var(--primary-glow)', borderColor: 'var(--primary)', color: 'var(--primary)' }}
            onClick={onOpenCart}
            style={{
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid var(--border)',
              cursor: 'pointer',
              color: 'var(--text)',
              position: 'relative',
              borderRadius: '50%',
              width: '42px',
              height: '42px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.3s ease'
            }}
          >
            <ShoppingBag size={18} />
            <span style={{
              position: 'absolute',
              top: '-4px',
              right: '-4px',
              background: 'var(--accent)',
              color: '#fff',
              fontSize: '0.65rem',
              fontWeight: 700,
              width: '18px',
              height: '18px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid var(--bg-deep)'
            }}>0</span>
          </motion.button>
        </div>
      </nav>
    </header>
  );
}
