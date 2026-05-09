import { useState } from 'react';
import { useNavigate, Link } from 'react-router';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card } from '../components/Card';
import { Alert } from '../components/Alert';
import { BookOpen } from 'lucide-react';

export function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await login({ username, password });
      navigate('/books');
    } catch {
      setError('Usuario ou senha invalidos');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <BookOpen className="w-12 h-12 text-blue-600 mb-3" />
          <h1 className="text-2xl font-bold text-gray-900">Bem-vindo a Livraria</h1>
          <p className="text-gray-600 mt-2">Faca login para continuar</p>
        </div>

        {error && (
          <Alert variant="error" onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 mt-6">
          <Input
            label="Usuario"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="seu usuario"
            required
          />

          <Input
            label="Senha"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="********"
            required
          />

          <Button type="submit" isLoading={isLoading} className="w-full">
            Entrar
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Nao tem uma conta?{' '}
            <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">
              Cadastre-se
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
}
