import { useEffect, useState } from 'react';
import { Book } from '../../api/types';
import { booksService } from '../../api/services/books.service';
import { useCart } from '../../contexts/CartContext';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Loader } from '../components/Loader';
import { Alert } from '../components/Alert';
import { Navbar } from '../components/Navbar';
import { ShoppingCart } from 'lucide-react';
import { toast } from 'sonner';

export function Books() {
  const [books, setBooks] = useState<Book[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const { addToCart } = useCart();

  useEffect(() => {
    void loadBooks();
  }, []);

  const loadBooks = async () => {
    try {
      setIsLoading(true);
      const data = await booksService.getBooks();
      setBooks(data);
    } catch {
      setError('Erro ao carregar livros');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddToCart = async (bookId: string) => {
    try {
      await addToCart(bookId, 1);
      toast.success('Livro adicionado ao carrinho!');
    } catch {
      toast.error('Erro ao adicionar ao carrinho');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Nossos Livros</h1>
          <p className="text-gray-600 mt-2">Explore nossa colecao e escolha seu proximo livro</p>
        </div>

        {error && (
          <Alert variant="error" onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {isLoading ? (
          <Loader size="lg" text="Carregando livros..." />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {books.map((book) => (
              <Card key={book.id} className="flex flex-col h-full">
                <div className="flex-1 flex flex-col">
                  <h3 className="font-bold text-lg text-gray-900 mb-2">{book.title}</h3>
                  <p className="text-gray-600 text-sm mb-4">Estoque: {book.stock}</p>

                  <div className="mt-auto">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-2xl font-bold text-blue-600">R$ {book.price.toFixed(2)}</span>
                    </div>

                    <Button onClick={() => handleAddToCart(book.id)} className="w-full" disabled={book.stock <= 0}>
                      <ShoppingCart className="w-4 h-4" />
                      {book.stock > 0 ? 'Adicionar ao Carrinho' : 'Sem estoque'}
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {!isLoading && books.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">Nenhum livro disponivel no momento</p>
          </div>
        )}
      </div>
    </div>
  );
}
