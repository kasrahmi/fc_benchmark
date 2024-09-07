# How to setup VM

## 1. Run Firecracker VM and SSH into it
```bash
bash scripts/run_fc.sh
ssh -i ./ubuntu/ubuntu-22.04.id_rsa root@172.16.0.2
```

## 2. Setup dependencies
### Install pheripherals

```bash
touch /var/lib/dpkg/status
apt-get update
apt-get install -y build-essential python3-pip htop git wget vim net-tools rsync
pip3 install grpcio grpcio-tools pyaes boto3 pillow scikit-learn
```

### Install Node

```bash
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
nvm install --lts
```