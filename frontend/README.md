# Livraria - Frontend

Sistema web responsivo para gerenciamento de uma livraria online, desenvolvido com React, TypeScript e Tailwind CSS.

## Funcionalidades

- **Autenticação**: Login e cadastro de usuários com JWT
- **Catálogo de Livros**: Listagem de livros disponíveis
- **Carrinho de Compras**: Adicionar/remover itens e visualizar subtotal
- **Cupons de Desconto**: Aplicar cupons e visualizar preview do desconto
- **Checkout**: Finalização de pedido com múltiplos métodos de pagamento (PIX, Cartão, Dinheiro)
- **Rotas Protegidas**: Navegação segura com autenticação obrigatória
- **Feedback Visual**: Loading states, mensagens de sucesso/erro e notificações

## Stack Tecnológica

- **React 18.3.1** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **React Router 7** - Roteamento
- **Axios** - Cliente HTTP
- **Tailwind CSS v4** - Estilização
- **Lucide React** - Ícones
- **Sonner** - Toast notifications
- **Vite** - Build tool

## Estrutura de Pastas

```
src/
├── api/
│   ├── client.ts              # Configuração do Axios + interceptors
│   ├── types.ts               # Tipos TypeScript
│   └── services/
│       ├── auth.service.ts    # Serviço de autenticação
│       ├── books.service.ts   # Serviço de livros
│       ├── cart.service.ts    # Serviço de carrinho
│       └── orders.service.ts  # Serviço de pedidos
├── contexts/
│   ├── AuthContext.tsx        # Contexto de autenticação
│   └── CartContext.tsx        # Contexto do carrinho
├── app/
│   ├── components/
│   │   ├── Alert.tsx          # Componente de alerta
│   │   ├── Button.tsx         # Componente de botão
│   │   ├── Card.tsx           # Componente de card
│   │   ├── Input.tsx          # Componente de input
│   │   ├── Loader.tsx         # Componente de loading
│   │   ├── Navbar.tsx         # Barra de navegação
│   │   └── ProtectedRoute.tsx # Componente de rota protegida
│   ├── pages/
│   │   ├── Login.tsx          # Página de login
│   │   ├── Register.tsx       # Página de cadastro
│   │   ├── Books.tsx          # Página de listagem de livros
│   │   ├── Cart.tsx           # Página do carrinho
│   │   └── Checkout.tsx       # Página de checkout
│   └── App.tsx                # Componente principal + rotas
└── styles/
    └── theme.css              # Estilos globais e tema
```

## Configuração e Instalação

### Pré-requisitos

- Node.js 18+ 
- pnpm (gerenciador de pacotes)

### Instalação

1. Clone o repositório

2. Instale as dependências:
```bash
pnpm install
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

4. Edite o arquivo `.env` com a URL da API:
```env
VITE_API_BASE_URL=https://livraria-api-staging-jar2vmuxea-uc.a.run.app/
```

Para desenvolvimento local com backend rodando localmente:
```env
VITE_API_BASE_URL=http://localhost:8080
```

### Executando o Projeto

O servidor de desenvolvimento já está rodando automaticamente. Abra o preview no navegador.

## Endpoints da API Utilizados

- `POST /api/v1/auth/register` - Cadastro de usuário
- `POST /api/v1/auth/login` - Login de usuário
- `GET /api/v1/books` - Listar livros
- `GET /api/v1/books/{id}` - Obter livro por ID
- `POST /api/v1/carts` - Criar carrinho
- `POST /api/v1/carts/{id}/items` - Adicionar item ao carrinho
- `DELETE /api/v1/carts/{id}/items/{book_id}` - Remover item do carrinho
- `POST /api/v1/orders/preview-discount` - Preview de desconto com cupom
- `POST /api/v1/orders/checkout` - Finalizar pedido

## Fluxo de Uso

1. **Registro/Login**: Usuário cria conta ou faz login
2. **Navegação**: JWT é armazenado no localStorage e enviado em todas requisições autenticadas
3. **Explorar Livros**: Visualiza catálogo e adiciona livros ao carrinho
4. **Carrinho**: Revisa itens, ajusta quantidades e remove produtos
5. **Checkout**: Aplica cupom de desconto (opcional) e escolhe método de pagamento
6. **Confirmação**: Pedido é processado e confirmação é exibida

## Tratamento de Erros

O sistema trata os seguintes códigos de erro:

- **401 Unauthorized**: Redireciona para login e limpa token
- **404 Not Found**: Exibe mensagem de recurso não encontrado
- **422 Unprocessable Entity**: Exibe erros de validação
- **500 Internal Server Error**: Exibe mensagem de erro genérica

## Autenticação

- JWT armazenado no `localStorage` com chave `authToken`
- Interceptor Axios adiciona `Authorization: Bearer <token>` automaticamente
- Rotas protegidas redirecionam para `/login` se não autenticado
- Logout limpa token e redireciona para login

## Responsividade

A aplicação é totalmente responsiva com breakpoints:

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

## Componentes Reutilizáveis

### Button
Botão customizável com variantes (primary, secondary, danger) e estado de loading.

### Input
Campo de entrada com label e mensagem de erro integrados.

### Card
Container com sombra e padding padrão.

### Alert
Mensagens de feedback com variantes (info, success, error, warning).

### Loader
Indicador de carregamento com tamanhos customizáveis.

### Navbar
Barra de navegação com contador de itens no carrinho e logout.

## Melhorias Futuras

- Paginação na listagem de livros
- Busca e filtros avançados
- Histórico de pedidos
- Gerenciamento de perfil do usuário
- Integração com gateway de pagamento real
- Testes unitários e E2E
- PWA (Progressive Web App)
- Dark mode

## Licença

MIT
