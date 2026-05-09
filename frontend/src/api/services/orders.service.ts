import { apiClient } from '../client';
import { PreviewDiscountRequest, PreviewDiscountResponse, CheckoutRequest, Order } from '../types';

export const ordersService = {
  async previewDiscount(data: PreviewDiscountRequest): Promise<PreviewDiscountResponse> {
    const response = await apiClient.post<PreviewDiscountResponse>('/api/v1/orders/preview-discount', data);
    return response.data;
  },

  async checkout(data: CheckoutRequest): Promise<Order> {
    const response = await apiClient.post<Order>('/api/v1/orders/checkout', data);
    return response.data;
  },
};
