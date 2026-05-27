import React from 'react';
import { motion } from 'motion/react';

const CATEGORIES = [
  { name: 'Shirts', img: '/images/shirt_1.jpg', count: 5 },
  { name: 'Pants', img: '/images/pant_1.jpg', count: 5 },
  { name: 'Watches', img: '/images/watch_1.jpg', count: 5 },
  { name: 'Jackets', img: '/images/jacket_1.jpg', count: 5 },
  { name: 'Shoes', img: '/images/shoes_1.jpg', count: 5 }
];

export default function Categories() {
  return (
    <section style={{ marginBottom: '5rem' }}>
      <div style={{ marginBottom: '3rem' }}>
        <p style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.75rem',
          color: 'var(--primary)',
          letterSpacing: '0.1rem',
          marginBottom: '0.6rem'
        }}>Browse by Category</p>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700 }}>
          Curated <span className="gradient-text">Collections</span>
        </h2>
        <div style={{ width: '50px', height: '3px', background: 'var(--primary)', marginTop: '0.8rem', borderRadius: '20px' }} />
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1.2rem',
        perspective: '1000px'
      }}>
        {CATEGORIES.map((cat, i) => (
          <motion.div
            key={cat.name}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ delay: i * 0.1, duration: 0.5 }}
            whileHover={{ rotateY: -5, rotateX: 3, scale: 1.04, boxShadow: '8px 12px 40px rgba(157,78,221,0.15)', zIndex: 2 }}
            style={{
              position: 'relative',
              height: '280px',
              borderRadius: '20px',
              overflow: 'hidden',
              cursor: 'pointer',
              border: '1px solid var(--border)',
              background: '#0c0c10'
            }}
          >
            <motion.img 
              src={`/api/products?category=${cat.name.toLowerCase()}`} // Placeholder logic
              alt={cat.name}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                filter: 'brightness(0.55)'
              }}
              whileHover={{ scale: 1.12, filter: 'brightness(0.7)' }}
              transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?auto=format&fit=crop&w=400&q=80' }} // Fallback
            />
            <div style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'flex-end',
              padding: '1.5rem',
              background: 'linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 60%)',
              pointerEvents: 'none'
            }}>
              <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.15rem', fontWeight: 700 }}>{cat.name}</h3>
              <p style={{ fontSize: '0.7rem', color: 'var(--muted)' }}>{cat.count} items</p>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
