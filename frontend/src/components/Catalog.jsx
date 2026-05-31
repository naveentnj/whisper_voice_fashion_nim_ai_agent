import React, { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import axios from 'axios';
import { ShoppingCart, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';

const CATEGORIES = [
  { id: 'all', label: 'All Products', icon: 'fa-border-all' },
  { id: 'shirt', label: 'Shirts', icon: 'fa-shirt' },
  { id: 'pant', label: 'Pants', icon: 'fa-socks' },
  { id: 'watch', label: 'Watches', icon: 'fa-clock' },
  { id: 'shoes', label: 'Shoes', icon: 'fa-shoe-prints' },
  { id: 'jacket', label: 'Jackets', icon: 'fa-person-shelter' }
];

export default function Catalog() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('all');
  const navigate = useNavigate();
  const { addToCart, user } = useCart();
  const [addedId, setAddedId] = useState(null);

  useEffect(() => {
    fetchProducts(activeCategory);
  }, [activeCategory]);

  const fetchProducts = async (cat) => {
    setLoading(true);
    try {
      const url = cat === 'all' ? '/api/products' : `/api/products?category=${cat}`;
      const res = await axios.get(url);
      setProducts(Array.isArray(res.data) ? res.data : res.data.products || []);
    } catch (err) {
      console.error('Error fetching products:', err);
    }
    setLoading(false);
  };

  return (
    <section id="catalog" style={{ marginBottom: '5rem' }}>
      <div style={{ marginBottom: '3rem' }}>
        <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--primary)', letterSpacing: '0.1rem', marginBottom: '0.6rem' }}>Full Inventory</p>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700 }}>All <span className="gradient-text">Products</span></h2>
        <div style={{ width: '50px', height: '3px', background: 'var(--primary)', marginTop: '0.8rem', borderRadius: '20px' }} />
      </div>

      <div className="responsive-catalog">
        {/* Sidebar */}
        <aside style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: '20px',
          padding: '1.5rem',
          height: 'fit-content',
          backdropFilter: 'blur(12px)',
          position: 'sticky',
          top: '90px'
        }}>
          <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '1rem', marginBottom: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.6rem' }}>Filter</h3>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            {CATEGORIES.map(c => (
              <li 
                key={c.id} 
                onClick={() => setActiveCategory(c.id)}
                style={{
                  padding: '0.7rem 0.9rem',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  fontSize: '0.82rem',
                  color: activeCategory === c.id ? '#fff' : 'var(--muted)',
                  background: activeCategory === c.id ? 'var(--primary)' : 'transparent',
                  fontWeight: activeCategory === c.id ? 500 : 400,
                  boxShadow: activeCategory === c.id ? '0 4px 15px var(--primary-glow)' : 'none',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.7rem'
                }}
              >
                {c.label}
              </li>
            ))}
          </ul>
        </aside>

        {/* Product Grid */}
        <div style={{ minHeight: '500px' }}>
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px', color: 'var(--muted)' }}>
              Loading Valenti Collections...
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1.5rem' }}>
              {products.map((p, i) => (
                <motion.div
                  key={p.id}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ delay: (i % 8) * 0.1 }}
                  whileHover={{ y: -8, borderColor: 'var(--primary-glow)', boxShadow: '0 12px 30px rgba(157,78,221,0.12)' }}
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border)',
                    borderRadius: '20px',
                    overflow: 'hidden',
                    backdropFilter: 'blur(12px)',
                    display: 'flex',
                    flexDirection: 'column',
                    cursor: 'pointer'
                  }}
                  onClick={() => navigate(`/product/${p.id}`)}
                >
                  <div style={{ height: '260px', position: 'relative', overflow: 'hidden', background: '#0c0c10' }}>
                    <motion.img 
                      src={p.image_url || 'https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?auto=format&fit=crop&w=400&q=80'} 
                      alt={p.name}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      whileHover={{ scale: 1.08 }}
                      transition={{ duration: 0.6 }}
                      onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?auto=format&fit=crop&w=400&q=80' }}
                    />
                    <div style={{
                      position: 'absolute', top: '12px', left: '12px',
                      background: 'rgba(6,6,8,0.6)', backdropFilter: 'blur(8px)',
                      border: '1px solid var(--border)', fontSize: '0.7rem',
                      fontWeight: 500, padding: '0.2rem 0.6rem', borderRadius: '10px',
                      textTransform: 'capitalize'
                    }}>
                      {p.category}
                    </div>
                  </div>
                  <div style={{ padding: '1.3rem', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                    <h4 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '1rem', marginBottom: '0.4rem', lineHeight: 1.4 }}>{p.name}</h4>
                    <p style={{ fontSize: '0.75rem', color: 'var(--muted)', lineHeight: 1.5, marginBottom: '1rem', flexGrow: 1 }}>{p.description}</p>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto' }}>
                      <span style={{ fontFamily: 'var(--font-display)', fontSize: '1.15rem', fontWeight: 800 }}>${p.price.toFixed(2)}</span>
                      <motion.button 
                        onClick={(e) => {
                          e.stopPropagation();
                          if (!user) { alert('Please sign in first to add items to your cart.'); return; }
                          addToCart(p.id, 1);
                          setAddedId(p.id);
                          setTimeout(() => setAddedId(null), 1200);
                        }}
                        whileHover={{ background: 'var(--primary)', borderColor: 'var(--primary)', color: '#fff', boxShadow: '0 0 15px var(--primary-glow)', scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                        style={{
                          background: addedId === p.id ? 'var(--primary)' : 'rgba(255,255,255,0.04)', border: '1px solid var(--border)',
                          color: addedId === p.id ? '#fff' : 'var(--text)', width: '38px', height: '38px', borderRadius: '50%',
                          display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
                          transition: 'background 0.3s'
                        }}
                      >
                        {addedId === p.id ? <Check size={16} /> : <ShoppingCart size={16} />}
                      </motion.button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
