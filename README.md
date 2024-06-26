# K8s Homelab

This project attepts to lay out a repeatable k8s deployment.
The motivation is primarily personal education.
To this end, the deployment provides the following capabilities:

- Continuous Delivery
- Certificate management
- Private DNS
- Encrypted persistent storage
- Disaster recovery
- Cluster metrics
- Identity services
- Secrets management
- Git
- Docker image registry
- Helm repository

## Project Architecture

```
.
├── ansible
│   ├── playbooks
│   └── roles
├── applications
│   ├── cert-manager
│   ├── coredns
│   ├── external-snapshotter
│   ├── gitea
│   ├── heimdall
│   ├── ingress-nginx
│   ├── keycloak
│   ├── kube-prometheus-stack
│   ├── longhorn
│   ├── master-app
│   └── metallb
└── deploy
    ├── base
    ├── bootstrap
    ├── overlays
    └── utility-manifests
```

- ansible
  - Contains a role and playbooks to simplify install and removal of the homelab deployment.
- applications
  - Collection of ArgoCD applications which will be deployed in the deployment's second stage.
- deploy
  - Contains Kustomize manifests to deploy argocd as well as depricated deployment resources.

## Building a cluster

TODO

### Boostrapping

First, it is important to prepare a values file for the role to use.
The best methhod is to copy the vars file at `ansible/roles/homelab/vars/main.yaml` to a safe location.

```
# Run local Ansible role
ansible-playbook ansible/playbooks/install.yaml -K
```

TODO: Proccess of creating overlay(s) in seperate repo to keep secrets seperate.
TODO: Discuss initial config of Keycloak: manual vs. automated vs. combined approach

### Post-Bootstrap Setup

TODO

### Resetting the Cluster

As long as the deployment has been deployed to microk8s, the cluster can be reset by running one script:

```
# This operation will destroy ALL persistent data!
deploy/bootstrap/reset-microk8s.sh
```

TODO: General guidelines for reset?

## Data Assurance

Longhorn + Velero doc: https://longhorn.io/docs/1.2.4/advanced-resources/cluster-restore/restore-to-a-new-cluster-using-velero/

### Create cluster backup

```
velero backup create my-backup-name --exclude-resources persistentvolumes,persistentvolumeclaims,backuptargets.longhorn.io,backupvolumes.longhorn.io,backups.longhorn.io,nodes.longhorn.io,volumes.longhorn.io,engines.longhorn.io,replicas.longhorn.io,backingimagedatasources.longhorn.io,backingimagemanagers.longhorn.io,backingimages.longhorn.io,sharemanagers.longhorn.io,instancemanagers.longhorn.io,engineimages.longhorn.io
```

### Restore cluster backup

```
# Do a cluster boostrap first
velero restore create --from-backup my-backup-name
```

### Ansible Variables Reference

| Variable | Description | Type | Default |
| -------- | ----------- | ---- | ------- | 
| domain | The domain which CoreDNS will serve internal services on | string | k8s.local |
| deployment_namespace_name | The namespace which wil be created for this deployment | string | core-deployment |
| projectPath | The path in which the project resides | string | /path/to/k8s-core-deployment |
| cert_manager.cert | Certificate bundle Cert Manager will use as its CA | string | ~ |
| cert_manager.key | Private key for Cert Manager's CA | string | ~ |
|  |  |  |
| gitea.email | Email for the Gitea user | string | ~ |
| gitea.password | Password for the Gitea user | string | ~ |
| gitea.pushRemote | Whether or not to push the project upon completion | bool | True |
| gitea.remoteName | Name of the git remote to be created | string | homelab |
| gitea.repoName | Name of the git repo to be created | string | k8s-control |
| gitea.username | Gitea username | string | ~ |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |