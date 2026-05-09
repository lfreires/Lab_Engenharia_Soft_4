import { apiClient } from '../client';
import { Cart, AddToCartRequest } from '../types';

export const cartService = {
  async createCart(): Promise<Cart> {
    const response = await apiClient.post<Cart>('/api/v1/carts');
    return response.data;
  },

  async getCart(cartId: string): Promise<Cart> {
    const response = await apiClient.get<Cart>(`/api/v1/carts/${cartId}`);
    return response.data;
  },

  async addItem(cartId: string, data: AddToCartRequest): Promise<Cart> {
    const response = await apiClient.post<Cart>(`/api/v1/carts/${cartId}/items`, data);
    return response.data;
  },

  async removeItem(cartId: string, bookId: string): Promise<Cart> {
    const response = await apiClient.delete<Cart>(`/api/v1/carts/${cartId}/items/${bookId}`);
    return response.data;
  },
};
