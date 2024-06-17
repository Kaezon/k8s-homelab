#!/bin/bash
cd "$(dirname "$0")"

set -e

if [ -z $1 ]; then
    NAMESPACE="default"
else
    NAMESPACE=$1
fi

# 0 if present, 1 otherwise
set +e
NAMESPACE_NOT_PRESENT=$(kubectl get namespace $NAMESPACE > /dev/null 2>&1)
set -e

# Should I require issuername and domain as environment vars?
# Or should i just take the repo as an arg/env ?

helm repo add metallb https://metallb.github.io/metallb
helm repo add coredns https://coredns.github.io/helm
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add gitea-charts https://dl.gitea.io/charts/
helm repo add longhorn https://charts.longhorn.io

if [ $NAMESPACE != "default" ] && [ NAMESPACE_NOT_PRESENT -ne 0 ]; then
    kubectl create namespace $NAMESPACE
fi

echo "[Bootstrap] Installing MetalLB..."
helm dependency update ../../applications/metallb
helm upgrade --install --create-namespace -n metallb-system metallb metallb/metallb -f ./values-metallb-base.yaml
helm upgrade --install --create-namespace -n metallb-system metallb ../../applications/metallb -f ./values-metallb.yaml --set addresses={"10.0.1.10-10.0.1.100"}
sleep 10

echo "[Bootstrap] Installing CoreDNS..."
helm dependency update ../../applications/coredns
helm upgrade --install --create-namespace -n $NAMESPACE coredns ../../applications/coredns
sleep 10

# Update cluster DNS so it can resolve the private domain
echo "[Bootstrap] Patching cluster DNS..."
python3 patch-corefile.py -d k8s.chimera 10.0.1.11

echo "[Bootstrap] Installing Ingress-Nginx..."
helm dependency update ../../applications/ingress-nginx
helm upgrade --install --create-namespace -n ingress-nginx ingress-nginx ../../applications/ingress-nginx
sleep 10

echo "[Bootstrap] Installing Certificate-Manager..."
helm dependency update ../../applications/cert-manager
helm upgrade --install --create-namespace -n cert-manager cert-manager jetstack/cert-manager --version 1.3.2 --set installCRDs=true,fullnameOverride=cert-manager
helm upgrade --install --create-namespace -n cert-manager cert-manager ../../applications/cert-manager -f ./values-cert-manager.yaml
sleep 10

echo "[Bootstrap] Installing Longhorn..."
helm dependency update ../../applications/longhorn
helm upgrade --install --create-namespace -n longhorn-system longhorn ../../applications/longhorn -f ../../applications/longhorn/values-bootstrap.yaml
sleep 30

echo "[Bootstrap] Installing Kube-Prometheus-Stack..."
helm dependency update ../../applications/kube-prometheus-stack
kubectl create namespace prometheus
kubectl apply -f ../homelab-overlay/production/secret-ca-bundle.yaml -n prometheus
helm upgrade --install --create-namespace -n prometheus kube-prometheus-stack ../../applications/kube-prometheus-stack
sleep 10

echo "[Bootstrap] Installing Keycloak..."
helm dependency update ../../applications/keycloak
cat ../../../homelab-overlay/production/patches/application-master.yaml | yq ".spec.source.helm.values" | yq -PM '{"keycloak": .keycloak}' > values-keycloak.yaml
helm upgrade --install --create-namespace -n $NAMESPACE keycloak ../../applications/keycloak -f values-keycloak.yaml
rm values-keycloak.yaml
sleep 20

echo "[Bootstrap] Installing Gitea..."
helm dependency update ../../applications/gitea
helm upgrade --install --create-namespace -n $NAMESPACE gitea ../../applications/gitea
sleep 30

# Push repo to cluster
echo "[Bootstrap] Setting up repo..."
python3 create-control-repo.py -u kaezon -p 7yE6poLAfmsn -r k8s-control --host https://git.k8s.chimera

# Apply overlay
echo "[Bootstrap] Done"
echo "Update your overlay with the argocd client secret and deploy ArgoCD! :)"