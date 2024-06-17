import argparse

import kubernetes

CORE_TEMPLATE = """
{}:53 {{
  forward . {}
  log
}}
"""

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--domain",
                    help="Domain to forward",
                    required=True)
parser.add_argument("ips",
                    help="IP of target DNS server(s)",
                    nargs='+')
args = parser.parse_args()


# Get coredns configmap
kubernetes.config.load_kube_config()
v1 = kubernetes.client.CoreV1Api()
configMap = v1.read_namespaced_config_map(name='coredns', namespace='kube-system')

# TODO: Can I check for existing forward directive and update it?
# Add forward directive to Corefile and patch the live ConfigMap
configMap.data['Corefile'] += CORE_TEMPLATE.format(
    args.domain,
    ' '.join(args.ips))
v1.patch_namespaced_config_map(name='coredns', namespace='kube-system', body=configMap)