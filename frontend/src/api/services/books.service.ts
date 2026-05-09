import { apiClient } from '../client';
import { Book } from '../types';

export const booksService = {
  async getBooks(): Promise<Book[]> {
    const response = await apiClient.get<Book[]>('/api/v1/books');
    return response.data;
  },

  async getBook(id: string): Promise<Book> {
    const response = await apiClient.get<Book>(`/api/v1/books/${id}`);
    return response.data;
  },

  async createBook(book: Omit<Book, 'id'>): Promise<Book> {
    const response = await apiClient.post<Book>('/api/v1/books', book);
    return response.data;
  },
};
