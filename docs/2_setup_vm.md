# How to setup VM

## 1. Run Firecracker VMM and VM, and SSH into it
```bash
# Run Firecracker VMM
bash scripts/fc_vmm.sh

# Run Firecracker VM
bash scripts/run_fc.sh
ssh -i ./ubuntu/ubuntu-22.04.id_rsa root@192.168.0.2
```

## 2. Setup dependencies
### Install Python Dependencies 

Run below on both Firecracker VM and Host OS

```bash
touch /var/lib/dpkg/status
apt-get update
apt-get install -y build-essential python3-pip htop git wget vim net-tools rsync
pip3 install grpcio grpcio-tools pyaes boto3 pillow scikit-learn pandas
```

### Install Node

```bash
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
nvm install --lts
```

### Move Workload to VM

```bash
rsync -Pav -e "ssh -i ./ubuntu/ubuntu-22.04.id_rsa" workload root@192.168.0.2:/root/.
```