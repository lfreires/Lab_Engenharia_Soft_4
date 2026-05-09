export interface User {
  username: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface Book {
  id: string;
  title: string;
  price: number;
  stock: number;
}

export interface Cart {
  id: string;
  items: CartItem[];
  total: number;
}

export interface CartItem {
  book_id: string;
  title: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface AddToCartRequest {
  book_id: string;
  quantity: number;
}

export interface PreviewDiscountRequest {
  cart_total: number;
  coupon_code: string;
}

export interface PreviewDiscountResponse {
  discounted_total: number;
  savings: number;
}

export interface CheckoutRequest {
  cart_id: string;
  payment_method: 'pix' | 'card' | 'cash';
  coupon_code?: string;
}

export interface Order {
  id: string;
  items: OrderItem[];
  total: number;
  status: string;
  coupon_code?: string | null;
  payment: Payment;
}

export interface OrderItem {
  book_id: string;
  title: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface Payment {
  order_id: string;
  amount: number;
  method: string;
  status: string;
}
