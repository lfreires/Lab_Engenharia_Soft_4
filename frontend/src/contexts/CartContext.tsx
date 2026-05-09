import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Cart } from '../api/types';
import { cartService } from '../api/services/cart.service';
import { handleApiError } from '../api/client';

interface CartContextType {
  cart: Cart | null;
  isLoading: boolean;
  error: string | null;
  createCart: () => Promise<void>;
  addToCart: (bookId: string, quantity: number) => Promise<void>;
  removeFromCart: (bookId: string) => Promise<void>;
  clearCart: () => void;
  clearError: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<Cart | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSavedCart = async () => {
      const savedCartId = localStorage.getItem('cartId');
      if (!savedCartId) return;

      try {
        const savedCart = await cartService.getCart(savedCartId);
        setCart(savedCart);
      } catch {
        localStorage.removeItem('cartId');
        setCart(null);
      }
    };

    void loadSavedCart();
  }, []);

  const createCart = async () => {
    try {
      setError(null);
      setIsLoading(true);
      const newCart = await cartService.createCart();
      setCart(newCart);
      localStorage.setItem('cartId', newCart.id);
    } catch (err) {
      const apiError = handleApiError(err);
      setError(apiError.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const addToCart = async (bookId: string, quantity: number) => {
    try {
      setError(null);
      setIsLoading(true);

      let currentCart = cart;
      if (!currentCart) {
        const newCart = await cartService.createCart();
        setCart(newCart);
        localStorage.setItem('cartId', newCart.id);
        currentCart = newCart;
      }

      const updatedCart = await cartService.addItem(currentCart.id, { book_id: bookId, quantity });
      setCart(updatedCart);
    } catch (err) {
      const apiError = handleApiError(err);
      setError(apiError.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const removeFromCart = async (bookId: string) => {
    if (!cart) return;

    try {
      setError(null);
      setIsLoading(true);
      const updatedCart = await cartService.removeItem(cart.id, bookId);
      setCart(updatedCart);
    } catch (err) {
      const apiError = handleApiError(err);
      setError(apiError.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const clearError = () => setError(null);
  const clearCart = () => {
    setCart(null);
    localStorage.removeItem('cartId');
  };

  return (
    <CartContext.Provider
      value={{
        cart,
        isLoading,
        error,
        createCart,
        addToCart,
        removeFromCart,
        clearCart,
        clearError,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
