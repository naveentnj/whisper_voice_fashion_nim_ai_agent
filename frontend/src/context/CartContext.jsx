import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const CartContext = createContext();

export function useCart() {
  return useContext(CartContext);
}

export function CartProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('valenti_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [cart, setCart] = useState({});       // { product_id: quantity }
  const [products, setProducts] = useState([]); // cached product list for lookups
  const [loginError, setLoginError] = useState('');

  // Fetch all products once for cart item lookups
  useEffect(() => {
    axios.get('/api/products').then(res => {
      setProducts(Array.isArray(res.data) ? res.data : res.data.products || []);
    }).catch(() => {});
  }, []);

  // Load cart from MongoDB when user logs in
  useEffect(() => {
    if (user) {
      localStorage.setItem('valenti_user', JSON.stringify(user));
      axios.get(`/api/cart/${user.username}`).then(res => {
        setCart(res.data.items || {});
      }).catch(() => {});
    } else {
      localStorage.removeItem('valenti_user');
      setCart({});
    }
  }, [user]);

  // Persist cart to MongoDB whenever it changes (debounced)
  const persistCart = useCallback((newCart) => {
    if (user) {
      axios.post('/api/cart', { username: user.username, items: newCart }).catch(() => {});
    }
  }, [user]);

  const login = async (username, password) => {
    setLoginError('');
    try {
      const res = await axios.post('/api/login', { username, password });
      setUser({ username: res.data.username });
      return true;
    } catch (err) {
      setLoginError(err.response?.data?.detail || 'Login failed');
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setCart({});
  };

  const addToCart = (productId, qty = 1) => {
    setCart(prev => {
      const updated = { ...prev, [productId]: (prev[productId] || 0) + qty };
      persistCart(updated);
      return updated;
    });
  };

  const removeFromCart = (productId) => {
    setCart(prev => {
      const updated = { ...prev };
      delete updated[productId];
      persistCart(updated);
      return updated;
    });
  };

  const updateQuantity = (productId, qty) => {
    if (qty <= 0) return removeFromCart(productId);
    setCart(prev => {
      const updated = { ...prev, [productId]: qty };
      persistCart(updated);
      return updated;
    });
  };

  const clearCart = () => {
    setCart({});
    if (user) {
      axios.delete(`/api/cart/${user.username}`).catch(() => {});
    }
  };

  const getProduct = (productId) => products.find(p => p.id === productId);

  const cartCount = Object.values(cart).reduce((sum, qty) => sum + qty, 0);
  const cartTotal = Object.entries(cart).reduce((sum, [pid, qty]) => {
    const p = getProduct(pid);
    return sum + (p ? p.price * qty : 0);
  }, 0);

  const cartItems = Object.entries(cart).map(([pid, qty]) => ({
    product: getProduct(pid),
    quantity: qty,
  })).filter(item => item.product);

  return (
    <CartContext.Provider value={{
      user, login, logout, loginError,
      cart, addToCart, removeFromCart, updateQuantity, clearCart,
      cartCount, cartTotal, cartItems, getProduct,
    }}>
      {children}
    </CartContext.Provider>
  );
}
