# Canary Deploy com Argo Rollouts (Kubernetes + Python)

Este repositório demonstra, de forma **prática e didática**, como funciona um **Canary Deploy** utilizando **Argo Rollouts**, **Kubernetes (kind)** e uma aplicação simples em **Python (FastAPI)**.

O foco deste laboratório é **entender o funcionamento interno do Argo Rollouts**, sem service mesh, sem Istio e sem métricas avançadas, evitando confusões comuns entre **deployment tradicional**, **canary deploy** e **load balancing**.

---

## 📌 Objetivo

Simular um **Canary Deploy controlado**, onde:

* **v1** é a versão estável da aplicação
* **v2** é criada como versão canary
* o tráfego de usuários **continua indo 100% para v1**
* o rollout ocorre em **etapas (steps)** com **pausas controladas**
* a nova versão **só começa a receber tráfego após ser promovida**
* o foco é **visualizar e entender o ciclo de vida do rollout**

Este cenário é ideal para:

* aprender Argo Rollouts do zero
* visualizar stable vs canary
* entender pausas, promoção e rollback

---

## 🧠 Conceito importante

> Neste cenário, o Canary **não divide tráfego**.  
> A divisão de tráfego **só acontece quando existe traffic routing configurado**.

Fluxo real deste laboratório:

```

Request
|
v
Kubernetes Service
|
└── v1 (stable)

v2 (canary)
└── aguardando promoção

```

📌 A versão **v2 só passa a receber tráfego após o rollout ser promovido**.

---

## ❌ O que este cenário NÃO é

Este laboratório **não utiliza**:

* Istio
* Service Mesh
* NGINX Ingress
* Prometheus ou métricas externas
* Divisão percentual de tráfego

📌 O foco aqui é **aprender Argo Rollouts**, não observabilidade nem malha de serviço.

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

````

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
````

---

### 2️⃣ Instalar o Argo Rollouts

```bash
kubectl create namespace argo-rollouts

kubectl apply -n argo-rollouts \
  -f https://raw.githubusercontent.com/argoproj/argo-rollouts/stable/manifests/install.yaml
```

Verifique a instalação:

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

Você poderá observar:

* pods **stable** e **canary**
* step atual do rollout
* pausas configuradas
* status geral do rollout

📌 Mesmo existindo pods canary, **eles não recebem tráfego ainda**.

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

* visualizar o progresso do rollout
* acompanhar pausas
* promover ou abortar o rollout
* entender visualmente stable vs canary

---

## 🧪 Simulando uma nova versão (v2)

Atualize a imagem no `rollout.yaml`:

```yaml
image: demo-app:2.0
```

E altere a variável de ambiente da aplicação:

```yaml
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

O rollout canary será iniciado automaticamente.

---

## 🧪 Testando a aplicação

Expose o service localmente:

```bash
kubectl port-forward svc/demo-app 8080:80
```

Faça requisições:

```bash
curl localhost:8080
```

Durante o rollout, você verá **apenas respostas da v1**:

```json
{
  "message": "Hello from Argo Rollouts",
  "version": "v1"
}
```

Após promover o rollout:

```bash
kubectl argo rollouts promote demo-rollout
```

As respostas passarão a ser da **v2**:

```json
{
  "message": "Hello from Argo Rollouts",
  "version": "v2"
}
```

Isso confirma que:

* o rollout foi promovido
* a v2 se tornou a nova versão estável
* o tráfego agora aponta para a nova versão
