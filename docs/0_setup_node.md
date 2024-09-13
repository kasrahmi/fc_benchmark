# Cloudlab
Get node with Intel CPU. Tested with `D430` and `xl170`.
Use profile `ntu-cloud/vhive-ubuntu22`

## Upgrade Linux Kernel to 6.1

```bash
sudo apt update  && sudo apt install -y build-essential gcc-12
sudo apt install --install-suggests linux-image-6.1.0-1036-oem
```

and reboot

## Clone Firecracker
```bash
git clone https://github.com/JooyoungPark73/firecracker
```

## Install Firecracker Build Dependencies

### Download Go
To keep consistency with vHive, use Go install script from the repo

### Install Docker

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Run the commands below line by line
```bash
sudo groupadd docker
sudo usermod -aG docker $USER 
newgrp docker
docker run hello-world
```

### Install awscli

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Set kvm permission

```bash
sudo apt-get install acl && sudo setfacl -m u:${USER}:rw /dev/kvm
```

```bash
[ $(stat -c "%G" /dev/kvm) = kvm ] && sudo usermod -aG kvm ${USER} \
&& echo "Access granted."
```

check by

```bash
[ -r /dev/kvm ] && [ -w /dev/kvm ] && echo "OK" || echo "FAIL"
```

if linux_version >=6.1, also run

```bash
sudo setfacl -m u:${USER}:rw /dev/userfaultfd
```

### Install dependency

```bash
sudo apt-get install clang cmake
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```