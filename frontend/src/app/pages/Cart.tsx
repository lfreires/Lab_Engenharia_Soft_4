import { useCart } from '../../contexts/CartContext';
import { Navbar } from '../components/Navbar';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Trash2, ShoppingBag, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';

export function Cart() {
  const { cart, removeFromCart, isLoading } = useCart();
  const navigate = useNavigate();

  const handleRemove = async (bookId: string) => {
    try {
      await removeFromCart(bookId);
      toast.success('Item removido do carrinho');
    } catch {
      toast.error('Erro ao remover item');
    }
  };

  const handleCheckout = () => {
    if (!cart?.items || cart.items.length === 0) {
      toast.error('Carrinho vazio');
      return;
    }
    navigate('/checkout');
  };

  const subtotal = cart?.total || 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Meu Carrinho</h1>
          <p className="text-gray-600 mt-2">
            {cart?.items?.length || 0} {(cart?.items?.length || 0) === 1 ? 'item' : 'itens'}
          </p>
        </div>

        {!cart?.items || cart.items.length === 0 ? (
          <Card className="text-center py-12">
            <ShoppingBag className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Seu carrinho esta vazio</h2>
            <p className="text-gray-600 mb-6">Adicione alguns livros para comecar!</p>
            <Button onClick={() => navigate('/books')}>Explorar Livros</Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-4">
              {cart.items.map((item) => (
                <Card key={item.book_id} className="flex gap-4">
                  <div className="flex-1 flex flex-col">
                    <h3 className="font-bold text-lg text-gray-900">{item.title}</h3>

                    <div className="mt-auto flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Quantidade: {item.quantity}</p>
                        <p className="text-sm text-gray-600">Unitario: R$ {item.unit_price.toFixed(2)}</p>
                        <p className="text-xl font-bold text-blue-600">R$ {item.subtotal.toFixed(2)}</p>
                      </div>

                      <Button variant="danger" onClick={() => handleRemove(item.book_id)} disabled={isLoading}>
                        <Trash2 className="w-4 h-4" />
                        Remover
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>

            <div className="lg:col-span-1">
              <Card className="sticky top-8">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Resumo do Pedido</h2>

                <div className="space-y-3 mb-6">
                  <div className="flex justify-between text-gray-600">
                    <span>Subtotal</span>
                    <span>R$ {subtotal.toFixed(2)}</span>
                  </div>
                  <div className="border-t pt-3 flex justify-between font-bold text-lg">
                    <span>Total</span>
                    <span className="text-blue-600">R$ {subtotal.toFixed(2)}</span>
                  </div>
                </div>

                <Button onClick={handleCheckout} className="w-full">
                  Finalizar Compra
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
