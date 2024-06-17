# Tennative order of operations:
# 1. ) Apply MetalLB
# 2. ) Apply CoreDNS
# 2a.) Apply modified kube-system CoreDNS CM
# 3. ) Apply Nginx Ingress
# 4. ) Apply Certificate Manager
# 5. ) Apply ArgoCD