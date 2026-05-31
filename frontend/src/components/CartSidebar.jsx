import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, ShoppingBag, Plus, Minus, Trash2 } from 'lucide-react';
import { useCart } from '../context/CartContext';

export default function CartSidebar({ isOpen, onClose }) {
  const { cartItems, cartTotal, cartCount, updateQuantity, removeFromCart, clearCart, user } = useCart();

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
              <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '1.15rem' }}>
                Your Cart {cartCount > 0 && <span style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>({cartCount})</span>}
              </h3>
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
              {!user ? (
                <div style={{ textAlign: 'center', padding: '2rem 0', color: 'var(--muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.8rem' }}>
                  <ShoppingBag size={40} style={{ opacity: 0.2 }} />
                  <p>Please sign in to use your cart.</p>
                </div>
              ) : cartItems.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem 0', color: 'var(--muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.8rem' }}>
                  <ShoppingBag size={40} style={{ opacity: 0.2 }} />
                  <p>Your cart is empty.</p>
                  <p style={{ fontSize: '0.7rem', fontStyle: 'italic', background: 'rgba(255,255,255,0.02)', border: '1px dashed var(--border)', padding: '0.5rem', borderRadius: '8px', marginTop: '0.8rem' }}>
                    Ask the AI: "Add Breeze Linen Summer Shirt to my cart"
                  </p>
                </div>
              ) : (
                cartItems.map(({ product, quantity }) => (
                  <motion.div
                    key={product.id}
                    layout
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    style={{
                      display: 'flex', gap: '1rem', padding: '0.8rem',
                      background: 'rgba(255,255,255,0.02)', borderRadius: '14px',
                      border: '1px solid var(--border)'
                    }}
                  >
                    <img 
                      src={product.image_url || 'https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?auto=format&fit=crop&w=100&q=80'}
                      alt={product.name}
                      style={{ width: '70px', height: '70px', borderRadius: '10px', objectFit: 'cover' }}
                      onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?auto=format&fit=crop&w=100&q=80' }}
                    />
                    <div style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                      <div>
                        <h4 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '0.82rem', lineHeight: 1.3 }}>{product.name}</h4>
                        <p style={{ fontSize: '0.65rem', color: 'var(--muted)', textTransform: 'capitalize' }}>{product.category}</p>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>${(product.price * quantity).toFixed(2)}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <motion.button 
                            whileTap={{ scale: 0.85 }}
                            onClick={() => updateQuantity(product.id, quantity - 1)}
                            style={{ width: '24px', height: '24px', borderRadius: '6px', border: '1px solid var(--border)', background: 'transparent', color: 'var(--text)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                          >
                            <Minus size={12} />
                          </motion.button>
                          <span style={{ fontSize: '0.8rem', fontWeight: 600, minWidth: '18px', textAlign: 'center' }}>{quantity}</span>
                          <motion.button 
                            whileTap={{ scale: 0.85 }}
                            onClick={() => updateQuantity(product.id, quantity + 1)}
                            style={{ width: '24px', height: '24px', borderRadius: '6px', border: '1px solid var(--border)', background: 'transparent', color: 'var(--text)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                          >
                            <Plus size={12} />
                          </motion.button>
                          <motion.button 
                            whileTap={{ scale: 0.85 }}
                            whileHover={{ color: 'var(--accent)' }}
                            onClick={() => removeFromCart(product.id)}
                            style={{ width: '24px', height: '24px', borderRadius: '6px', border: 'none', background: 'transparent', color: 'var(--muted)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', marginLeft: '0.3rem' }}
                          >
                            <Trash2 size={12} />
                          </motion.button>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
            
            <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border)', background: 'rgba(0,0,0,0.2)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1rem', fontWeight: 600, marginBottom: '1.2rem' }}>
                <span>Subtotal:</span>
                <span style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem', color: 'var(--primary)', fontWeight: 800 }}>${cartTotal.toFixed(2)}</span>
              </div>
              {cartItems.length > 0 && (
                <div style={{ display: 'flex', gap: '0.6rem' }}>
                  <motion.button
                    whileHover={{ borderColor: 'var(--accent)' }}
                    whileTap={{ scale: 0.98 }}
                    onClick={clearCart}
                    style={{
                      flex: '0 0 auto',
                      padding: '0.85rem 1rem',
                      borderRadius: '14px',
                      fontWeight: 600,
                      fontSize: '0.8rem',
                      cursor: 'pointer',
                      fontFamily: 'var(--font-sans)',
                      background: 'transparent',
                      color: 'var(--muted)',
                      border: '1px solid var(--border)'
                    }}
                  >
                    Clear
                  </motion.button>
                  <motion.button 
                    whileHover={{ y: -2, boxShadow: '0 0 25px var(--accent-glow)' }}
                    whileTap={{ scale: 0.98 }}
                    style={{
                      flex: 1,
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
                    Checkout
                  </motion.button>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
