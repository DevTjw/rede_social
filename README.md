# 📘 **Rede Social Interna**

Uma plataforma interna no estilo de rede social, com feeds personalizados, sistema de seguidores, troca de mensagens em tempo real (WebSockets) e perfis de usuários.
Projetada para empresas, equipes e comunidades que precisam de comunicação rápida, organizada e centralizada.

---

## 📂 **Funcionalidades Principais**

### 🔐 Autenticação e Perfis

* Cadastro, login e logout
* Django Authentication integrado
* Perfis totalmente personalizados
* Controle de permissões (usuário, cliente, administrador)

---

### 📰 Feed e Postagens

* Criação de posts com texto, imagens e anexos
* Curtidas e comentários
* Feed baseado nos usuários seguidos
* Página de exploração para descobrir novos perfis

---

### 🤝 Sistema de Seguidores

* Seguir e deixar de seguir usuários
* Feed dinâmico gerado a partir dos perfis acompanhados
* Notificações internas (opcional)

---

### 💬 Mensagens Internas (Tempo Real)

* Chat individual entre usuários
* Restrição opcional: apenas usuários conectados ou que se seguem
* Suporte a WebSockets (**Django Channels**)
* Histórico de mensagens salvo no banco
* Indicação de status online/offline (opcional)

---

### 🧩 API + Front-end

* Views organizadas seguindo boas práticas
* Templates responsivos com **Bootstrap 5**
* Rotas limpas e padronizadas
* API REST opcional com Django REST Framework

---

## 🛠️ **Tecnologias Utilizadas**

| Componente                         | Detalhes                                         |
| ---------------------------------- | ------------------------------------------------ |
| **Framework**                      | Django 4+                                        |
| **Linguagem**                      | Python 3.11 – 3.14                               |
| **Banco de Dados**                 | SQLite (desenvolvimento) / PostgreSQL (produção) |
| **WebSockets**                     | Django Channels                                  |
| **Broker**                         | Redis                                            |
| **Tarefas Assíncronas (opcional)** | Celery                                           |
| **Frontend**                       | HTML, CSS, Bootstrap 5                           |

---

## 📦 **Instalação e Configuração**

### 1) Clone o repositório

```bash
git clone https://github.com/devtjw/rede-social.git
cd rede-social-interna
```

### 2) Instale as dependências

```bash
pip install -r requirements.txt
```

### 3) Execute as migrações

```bash
python manage.py migrate
```

### 4) Inicie o servidor

```bash
python manage.py runserver
```

### 5) Caso utilize WebSockets (Channels)

```bash
daphne projeto.asgi:application
```

---

## 📅 **Roadmap**

* [ ] Sistema de notificações
* [ ] Grupos / comunidades internas
* [ ] Chats em grupo
* [ ] Modo escuro
* [ ] Upload de vídeos
* [ ] API REST completa (DRF)
* [ ] Testes automatizados

---

## 🧑‍💻 **Contribuições**

Contribuições são bem-vindas!
Para mudanças maiores, abra uma *issue* antes para discutirmos a proposta.

---

## 📜 **Licença**

Distribuído sob a **MIT License**.

---

