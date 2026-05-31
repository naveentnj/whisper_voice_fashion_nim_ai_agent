import React, { useState } from 'react';
import { ShoppingBag, User, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useCart } from '../context/CartContext';

export default function Header({ onOpenCart }) {
  const { user, login, logout, loginError, cartCount } = useCart();
  const [showLogin, setShowLogin] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    const ok = await login(username, password);
    if (ok) {
      setShowLogin(false);
      setUsername('');
      setPassword('');
    }
  };

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

          {/* User Auth Button */}
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 600 }}>
                {user.username}
              </span>
              <motion.button
                whileHover={{ scale: 1.1, color: 'var(--accent)' }}
                whileTap={{ scale: 0.9 }}
                onClick={logout}
                title="Logout"
                style={{
                  background: 'none', border: 'none', color: 'var(--muted)',
                  cursor: 'pointer', display: 'flex', alignItems: 'center'
                }}
              >
                <LogOut size={16} />
              </motion.button>
            </div>
          ) : (
            <motion.button
              whileHover={{ y: -2, borderColor: 'var(--primary)', color: 'var(--primary)' }}
              onClick={() => setShowLogin(true)}
              style={{
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid var(--border)',
                cursor: 'pointer',
                color: 'var(--text)',
                borderRadius: '24px',
                padding: '0.4rem 0.8rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                fontSize: '0.75rem',
                transition: 'all 0.3s ease'
              }}
            >
              <User size={14} /> Sign In
            </motion.button>
          )}
          
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
              background: cartCount > 0 ? 'var(--accent)' : 'var(--muted)',
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
            }}>{cartCount}</span>
          </motion.button>
        </div>
      </nav>

      {/* Login Modal */}
      <AnimatePresence>
        {showLogin && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowLogin(false)}
              style={{
                position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
                zIndex: 999, backdropFilter: 'blur(4px)'
              }}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              style={{
                position: 'fixed', top: '50%', left: '50%',
                transform: 'translate(-50%, -50%)',
                background: 'var(--bg-card)', border: '1px solid var(--border)',
                borderRadius: '20px', padding: '2.5rem', width: '340px',
                zIndex: 1000, backdropFilter: 'blur(20px)',
                boxShadow: '0 20px 50px rgba(0,0,0,0.5)'
              }}
            >
              <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.4rem', marginBottom: '0.4rem' }}>
                Welcome Back
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginBottom: '1.5rem' }}>
                Sign in to your Valenti account
              </p>
              <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <input
                  type="text"
                  placeholder="Username"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  style={{
                    padding: '0.7rem 1rem', borderRadius: '12px',
                    border: '1px solid var(--border)', background: 'rgba(0,0,0,0.3)',
                    color: 'var(--text)', fontSize: '0.85rem', outline: 'none',
                    fontFamily: 'var(--font-sans)'
                  }}
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  style={{
                    padding: '0.7rem 1rem', borderRadius: '12px',
                    border: '1px solid var(--border)', background: 'rgba(0,0,0,0.3)',
                    color: 'var(--text)', fontSize: '0.85rem', outline: 'none',
                    fontFamily: 'var(--font-sans)'
                  }}
                />
                {loginError && (
                  <p style={{ fontSize: '0.75rem', color: 'var(--accent)', textAlign: 'center' }}>{loginError}</p>
                )}
                <motion.button
                  type="submit"
                  whileHover={{ scale: 1.02, boxShadow: '0 0 20px var(--primary-glow)' }}
                  whileTap={{ scale: 0.98 }}
                  style={{
                    padding: '0.8rem', borderRadius: '12px', border: 'none',
                    background: 'linear-gradient(135deg, var(--primary), var(--accent))',
                    color: '#fff', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer',
                    fontFamily: 'var(--font-sans)'
                  }}
                >
                  Sign In
                </motion.button>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </header>
  );
}
