# Canary Deploy com Argo Rollouts (Kubernetes + Python)

Este repositório demonstra, de forma **prática e didática**, como funciona um **Canary Deploy** utilizando **Argo Rollouts**, **Kubernetes (kind)** e uma aplicação simples em **Python (FastAPI)**.

O foco é **entender o comportamento real de um rollout canary**, sem service mesh, sem Istio e sem métricas avançadas, evitando confusões comuns entre **deployment tradicional**, **canary** e **load balancing**.

---

## 📌 Objetivo

Simular um cenário real onde:

* **v1** é a versão estável da aplicação
* **v2** é uma nova versão sendo liberada gradualmente
* o tráfego é **dividido progressivamente** entre v1 e v2
* o rollout ocorre em **etapas (steps)** com **pausas controladas**
* a nova versão só se torna estável após completar todas as etapas

Esse padrão é amplamente utilizado para:

* reduzir risco em deploys
* validar novas versões com usuários reais
* liberar funcionalidades de forma controlada
* permitir rollback rápido
* aumentar a confiabilidade do sistema

---

## 🧠 Conceito importante

> Canary Deploy **divide tráfego**
> Canary Deploy **não copia requisições**

Fluxo real:

```
Request
   |
   v
Kubernetes Service
   |
   ├── v1 (stable)
   |
   └── v2 (canary)
```

Durante o rollout:

* parte dos usuários recebe resposta da v1
* parte dos usuários recebe resposta da v2
* a proporção muda conforme os steps configurados

---

## ❌ O que este cenário NÃO é

Este laboratório **não utiliza**:

* Istio
* Service Mesh
* Prometheus ou métricas externas
* Load balancer avançado

📌 O foco aqui é **aprender Argo Rollouts**, não observabilidade ou malha de serviço.

---

## 📁 Estrutura do projeto

```
argo-rollouts-lab/
├── app/
│   ├── main.py
│   └── requirements.txt
├── Dockerfile
├── k8s/
│   ├── rollout.yaml
│   └── service.yaml
├── kind-cluster.yaml
└── README.md
```

---

## ⚙️ Pré-requisitos

* Docker
* Kubernetes (Kind)
* kubectl
* Argo Rollouts CLI (`kubectl-argo-rollouts`)

---

## 🚀 Passo a passo

### 1️⃣ Criar o cluster Kubernetes (kind)

```bash
kind create cluster --name argo --config kind-cluster.yaml
```

---

### 2️⃣ Instalar o Argo Rollouts

```bash
kubectl create namespace argo-rollouts

kubectl apply -n argo-rollouts \
  -f https://raw.githubusercontent.com/argoproj/argo-rollouts/stable/manifests/install.yaml
```

Instale o plugin CLI:

```bash
kubectl argo rollouts version
```

---

### 3️⃣ Build da imagem da aplicação (v1)

```bash
docker build -t demo-app:1.0 .
kind load docker-image demo-app:1.0 --name argo
```

---

### 4️⃣ Aplicar os manifests Kubernetes

```bash
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/rollout.yaml
```

---

## 🔎 Observando o rollout

### Via CLI

```bash
kubectl argo rollouts get rollout demo-rollout --watch
```

Informações observadas:

* pods **stable** e **canary**
* step atual do rollout
* peso do tráfego
* status geral

---

### Via Dashboard Web (Frontend)

```bash
kubectl argo rollouts dashboard
```

Acesse no navegador:

```
http://localhost:3100
```

No dashboard é possível:

* visualizar o progresso do canary
* acompanhar pausas
* promover ou abortar o rollout
* entender visualmente stable vs canary

---

## 🧪 Simulando uma nova versão (v2)

Atualize a imagem no `rollout.yaml`:

```yaml
image: demo-app:2.0
APP_VERSION: "v2"
```

Build e carregue a imagem:

```bash
docker build -t demo-app:2.0 .
kind load docker-image demo-app:2.0 --name argo
```

Reaplique o rollout:

```bash
kubectl apply -f k8s/rollout.yaml
```

O canary será iniciado automaticamente.

---

## 🧪 Testando a aplicação

Expose o service localmente:

```bash
kubectl port-forward svc/demo-app 8080:80
```

Faça múltiplas requisições:

```bash
curl localhost:8080
```

Você observará respostas alternando entre:

```json
{
  "message": "Hello from Argo Rollouts",
  "version": "v1"
}
```

e

```json
{
  "message": "Hello from Argo Rollouts",
  "version": "v2"
}
```

Isso confirma a **divisão de tráfego do canary**.

---

## ✅ Boas práticas

* começar com percentuais baixos (10% ou 20%)
* usar pausas para validação manual
* manter rollback simples e rápido
* visualizar o rollout antes de automatizar métricas
