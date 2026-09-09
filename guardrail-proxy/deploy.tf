# Terraform: Sovereign Guardrail Deployment
provider "naver" {
  region = "kr-central-1"
}

resource "naver_cloud_gateway" "sovereign_proxy" {
  name = "pi-compliance-gateway"
  port = 8080
  
  tags = {
    Environment = "production"
    Compliance  = "PIPA-2026"
  }
}

# Ansible: System Hardening
- hosts: all
  tasks:
    - name: install guardrail binary
      copy:
        src: ./guardrail-proxy
        dest: /usr/local/bin/guardrail
        mode: '0755'
    - name: setup service
      systemd:
        name: guardrail
        enabled: yes
        state: started
