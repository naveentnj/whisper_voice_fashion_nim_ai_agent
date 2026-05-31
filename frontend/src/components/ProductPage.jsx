import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import axios from 'axios';
import { ArrowLeft, ShoppingCart, Check } from 'lucide-react';
import { useCart } from '../context/CartContext';

export default function ProductPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [added, setAdded] = useState(false);
  const { addToCart, user } = useCart();

  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true);
      try {
        const res = await axios.get('/api/products');
        const productsList = Array.isArray(res.data) ? res.data : res.data.products || [];
        const found = productsList.find(p => p.id === id);
        setProduct(found);
      } catch (err) {
        console.error('Error fetching product:', err);
      }
      setLoading(false);
    };
    fetchProduct();
  }, [id]);

  if (loading) {
    return (
      <div style={{ height: '70vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--muted)' }}>
        Loading product details...
      </div>
    );
  }

  if (!product) {
    return (
      <div style={{ height: '70vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text)' }}>
        <h2>Product not found.</h2>
        <button onClick={() => navigate('/')} style={{ marginTop: '1rem', padding: '0.5rem 1rem', background: 'var(--primary)', border: 'none', color: '#fff', borderRadius: '10px', cursor: 'pointer' }}>
          Back to Catalog
        </button>
      </div>
    );
  }

  return (
    <motion.section 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      style={{ maxWidth: '1200px', margin: '4rem auto', padding: '0 2rem', minHeight: '60vh' }}
    >
      <button 
        onClick={() => navigate('/')} 
        style={{ 
          background: 'transparent', border: 'none', color: 'var(--muted)', cursor: 'pointer', 
          display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem', fontSize: '0.9rem'
        }}
      >
        <ArrowLeft size={16} /> Back to collections
      </button>

      <div className="responsive-product">
        <motion.div 
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          style={{ borderRadius: '20px', overflow: 'hidden', border: '1px solid var(--border)' }}
        >
          <img 
            src={product.image || 'https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?auto=format&fit=crop&w=800&q=80'} 
            alt={product.name} 
            style={{ width: '100%', height: '100%', objectFit: 'cover', minHeight: '500px' }}
            onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?auto=format&fit=crop&w=800&q=80' }}
          />
        </motion.div>

        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.1rem', marginBottom: '1rem' }}>
            {product.category}
          </p>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '3rem', fontWeight: 700, marginBottom: '1.5rem', lineHeight: 1.1 }}>
            {product.name}
          </h1>
          <p style={{ fontSize: '1.1rem', color: 'var(--muted)', lineHeight: 1.6, marginBottom: '2rem' }}>
            {product.description}
          </p>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 800, marginBottom: '2rem' }}>
            ${product.price.toFixed(2)}
          </div>

          <motion.button 
            whileHover={{ scale: 1.02, boxShadow: '0 0 20px var(--primary-glow)' }}
            whileTap={{ scale: 0.98 }}
            onClick={(e) => {
              e.stopPropagation();
              if (!user) { alert('Please sign in first to add items to your cart.'); return; }
              addToCart(product.id, 1);
              setAdded(true);
              setTimeout(() => setAdded(false), 1500);
            }}
            style={{ 
              background: 'linear-gradient(90deg, var(--primary), var(--accent))', 
              border: 'none', color: '#fff', padding: '1rem 2rem', borderRadius: '15px', 
              fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', 
              justifyContent: 'center', gap: '1rem', cursor: 'pointer' 
            }}
          >
            <ShoppingCart size={20} /> {added ? 'Added!' : 'Add to Cart'}
          </motion.button>

          <p style={{ marginTop: '2rem', fontSize: '0.85rem', color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: product.stock > 0 ? '#10b981' : '#ef4444' }} />
            {product.stock > 0 ? `${product.stock} units in stock` : 'Out of stock'}
          </p>
        </div>
      </div>
    </motion.section>
  );
}
