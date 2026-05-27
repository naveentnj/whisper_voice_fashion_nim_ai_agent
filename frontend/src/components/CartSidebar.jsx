import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, ShoppingBag } from 'lucide-react';

export default function CartSidebar({ isOpen, onClose }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0,0,0,0.6)',
              zIndex: 999,
              backdropFilter: 'blur(4px)'
            }}
          />
          <motion.div
            initial={{ right: '-450px' }}
            animate={{ right: 0 }}
            exit={{ right: '-450px' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            style={{
              position: 'fixed',
              top: 0,
              right: 0,
              width: '380px',
              height: '100vh',
              background: 'var(--bg-card)',
              borderLeft: '1px solid var(--border)',
              boxShadow: '-10px 0 30px rgba(0,0,0,0.5)',
              zIndex: 1000,
              display: 'flex',
              flexDirection: 'column',
              backdropFilter: 'blur(20px)'
            }}
          >
            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '1.15rem' }}>Your Shopping Cart</h3>
              <motion.button 
                whileHover={{ color: 'var(--accent)', scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={onClose}
                style={{ background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </motion.button>
            </div>
            
            <div style={{ padding: '1.5rem', flexGrow: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ textAlign: 'center', padding: '2rem 0', color: 'var(--muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.8rem' }}>
                <ShoppingBag size={40} style={{ opacity: 0.2 }} />
                <p>Your cart is empty.</p>
                <p style={{ fontSize: '0.7rem', fontStyle: 'italic', background: 'rgba(255,255,255,0.02)', border: '1px dashed var(--border)', padding: '0.5rem', borderRadius: '8px', marginTop: '0.8rem' }}>
                  Ask the AI: "Add Breeze Linen Summer Shirt to my cart"
                </p>
              </div>
            </div>
            
            <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border)', background: 'rgba(0,0,0,0.2)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1rem', fontWeight: 600, marginBottom: '1.2rem' }}>
                <span>Subtotal:</span>
                <span style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem', color: 'var(--primary)', fontWeight: 800 }}>$0.00</span>
              </div>
              <motion.button 
                whileHover={{ y: -2, boxShadow: '0 0 25px var(--accent-glow)' }}
                whileTap={{ scale: 0.98 }}
                style={{
                  width: '100%',
                  padding: '0.85rem 1.6rem',
                  borderRadius: '14px',
                  fontWeight: 600,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  fontFamily: 'var(--font-sans)',
                  background: 'linear-gradient(135deg, var(--accent) 0%, #d8006b 100%)',
                  color: '#fff',
                  border: 'none'
                }}
              >
                Proceed to Checkout
              </motion.button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
