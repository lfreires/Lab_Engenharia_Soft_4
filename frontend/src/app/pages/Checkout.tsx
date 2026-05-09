import { useState } from 'react';
import { useCart } from '../../contexts/CartContext';
import { ordersService } from '../../api/services/orders.service';
import { Navbar } from '../components/Navbar';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Alert } from '../components/Alert';
import { CreditCard, Smartphone, Wallet, Tag, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';

type PaymentMethod = 'pix' | 'card' | 'cash';

export function Checkout() {
  const { cart } = useCart();
  const navigate = useNavigate();

  const [couponCode, setCouponCode] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('card');
  const [isLoadingCoupon, setIsLoadingCoupon] = useState(false);
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [discount, setDiscount] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const subtotal = cart?.total || 0;
  const total = subtotal - discount;

  const handleApplyCoupon = async () => {
    if (!cart || !couponCode.trim()) return;

    try {
      setError('');
      setIsLoadingCoupon(true);
      const preview = await ordersService.previewDiscount({
        cart_total: subtotal,
        coupon_code: couponCode,
      });
      setDiscount(preview.savings);
      toast.success('Cupom aplicado com sucesso!');
    } catch {
      setDiscount(0);
      toast.error('Cupom invalido ou expirado');
    } finally {
      setIsLoadingCoupon(false);
    }
  };

  const handleCheckout = async () => {
    if (!cart) return;

    try {
      setError('');
      setIsCheckingOut(true);
      await ordersService.checkout({
        cart_id: cart.id,
        payment_method: paymentMethod,
        coupon_code: couponCode || undefined,
      });
      setSuccess(true);
      localStorage.removeItem('cartId');
      toast.success('Pedido realizado com sucesso!');

      setTimeout(() => {
        navigate('/books');
      }, 3000);
    } catch {
      setError('Erro ao finalizar pedido. Tente novamente.');
      toast.error('Erro ao finalizar pedido');
    } finally {
      setIsCheckingOut(false);
    }
  };

  if (!cart?.items || cart.items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-5xl mx-auto px-4 py-8">
          <Alert variant="warning">
            Seu carrinho esta vazio. Adicione alguns livros antes de finalizar o pedido.
          </Alert>
          <div className="mt-4">
            <Button onClick={() => navigate('/books')}>Explorar Livros</Button>
          </div>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-2xl mx-auto px-4 py-16">
          <Card className="text-center py-12">
            <CheckCircle className="w-20 h-20 text-green-600 mx-auto mb-6" />
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Pedido Confirmado!</h1>
            <p className="text-gray-600 mb-2">Seu pedido foi realizado com sucesso.</p>
            <p className="text-gray-600 mb-8">Voce sera redirecionado em instantes...</p>
            <Button onClick={() => navigate('/books')}>Voltar para a Loja</Button>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Finalizar Compra</h1>
          <p className="text-gray-600 mt-2">Revise seu pedido e escolha a forma de pagamento</p>
        </div>

        {error && (
          <Alert variant="error" onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <h2 className="text-xl font-bold text-gray-900 mb-4">Itens do Pedido</h2>
              <div className="space-y-3">
                {cart.items.map((item) => (
                  <div key={item.book_id} className="flex justify-between items-center py-2 border-b last:border-0">
                    <div>
                      <p className="font-medium text-gray-900">{item.title}</p>
                      <p className="text-sm text-gray-600">Quantidade: {item.quantity}</p>
                    </div>
                    <p className="font-semibold text-gray-900">R$ {item.subtotal.toFixed(2)}</p>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <h2 className="text-xl font-bold text-gray-900 mb-4">Cupom de Desconto</h2>
              <div className="flex gap-2">
                <Input
                  placeholder="Digite seu cupom"
                  value={couponCode}
                  onChange={(e) => setCouponCode(e.target.value)}
                  className="flex-1"
                />
                <Button onClick={handleApplyCoupon} isLoading={isLoadingCoupon} variant="secondary">
                  <Tag className="w-4 h-4" />
                  Aplicar
                </Button>
              </div>
              {discount > 0 && (
                <Alert variant="success" className="mt-4">
                  Desconto de R$ {discount.toFixed(2)} aplicado!
                </Alert>
              )}
            </Card>

            <Card>
              <h2 className="text-xl font-bold text-gray-900 mb-4">Metodo de Pagamento</h2>
              <div className="space-y-3">
                <label className={`flex items-center gap-3 p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  paymentMethod === 'card' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'
                }`}>
                  <input
                    type="radio"
                    name="payment"
                    value="card"
                    checked={paymentMethod === 'card'}
                    onChange={() => setPaymentMethod('card')}
                    className="w-4 h-4 text-blue-600"
                  />
                  <CreditCard className="w-5 h-5 text-gray-700" />
                  <span className="font-medium">Cartao</span>
                </label>

                <label className={`flex items-center gap-3 p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  paymentMethod === 'pix' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'
                }`}>
                  <input
                    type="radio"
                    name="payment"
                    value="pix"
                    checked={paymentMethod === 'pix'}
                    onChange={() => setPaymentMethod('pix')}
                    className="w-4 h-4 text-blue-600"
                  />
                  <Smartphone className="w-5 h-5 text-gray-700" />
                  <span className="font-medium">PIX</span>
                </label>

                <label className={`flex items-center gap-3 p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  paymentMethod === 'cash' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'
                }`}>
                  <input
                    type="radio"
                    name="payment"
                    value="cash"
                    checked={paymentMethod === 'cash'}
                    onChange={() => setPaymentMethod('cash')}
                    className="w-4 h-4 text-blue-600"
                  />
                  <Wallet className="w-5 h-5 text-gray-700" />
                  <span className="font-medium">Dinheiro</span>
                </label>
              </div>
            </Card>
          </div>

          <div className="lg:col-span-1">
            <Card className="sticky top-8">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Resumo</h2>

              <div className="space-y-3 mb-6">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span>R$ {subtotal.toFixed(2)}</span>
                </div>

                {discount > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Desconto</span>
                    <span>- R$ {discount.toFixed(2)}</span>
                  </div>
                )}

                <div className="border-t pt-3 flex justify-between font-bold text-xl">
                  <span>Total</span>
                  <span className="text-blue-600">R$ {total.toFixed(2)}</span>
                </div>
              </div>

              <Button onClick={handleCheckout} isLoading={isCheckingOut} className="w-full" disabled={!paymentMethod}>
                Confirmar Pedido
              </Button>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
