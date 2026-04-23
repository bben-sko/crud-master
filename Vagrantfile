# -*- mode: ruby -*-
# vi: set ft=ruby :

def load_env_file(path)
  env = {}
  return env unless File.exist?(path)

  File.readlines(path).each do |line|
    stripped = line.strip
    next if stripped.empty? || stripped.start_with?("#")

    key, value = stripped.split("=", 2)
    env[key] = value
  end

  env
end

env = load_env_file(File.expand_path(".env", __dir__))

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.synced_folder ".", "/vagrant", disabled: true

  common_env = {
    "GATEWAY_APP_DIR" => "/home/vagrant/api-gateway-app",
    "INVENTORY_APP_DIR" => "/home/vagrant/inventory-app",
    "BILLING_APP_DIR" => "/home/vagrant/billing-app",
  }.merge(env)

  config.vm.define "gateway-vm" do |gateway|
    gateway.vm.hostname = "gateway-vm"
    gateway.vm.network "private_network", ip: env.fetch("GATEWAY_VM_IP", "192.168.56.10")
    gateway.vm.network "forwarded_port", guest: env.fetch("GATEWAY_PORT", "3000").to_i, host: env.fetch("GATEWAY_PORT", "3000").to_i
    gateway.vm.synced_folder "./srcs/api-gateway-app", "/home/vagrant/api-gateway-app"

    gateway.vm.provider "virtualbox" do |vb|
      vb.memory = 2048
      vb.cpus = 1
    end

    gateway.vm.provision "shell", path: "./scripts/global.sh", env: common_env
    gateway.vm.provision "shell", path: "./scripts/gateway.sh", env: common_env
  end

  config.vm.define "inventory-vm" do |inventory|
    inventory.vm.hostname = "inventory-vm"
    inventory.vm.network "private_network", ip: env.fetch("INVENTORY_VM_IP", "192.168.56.11")
    inventory.vm.network "forwarded_port", guest: env.fetch("INVENTORY_PORT", "8080").to_i, host: env.fetch("INVENTORY_PORT", "8080").to_i
    inventory.vm.synced_folder "./srcs/inventory-app", "/home/vagrant/inventory-app"

    inventory.vm.provider "virtualbox" do |vb|
      vb.memory = 2048
      vb.cpus = 1
    end

    inventory.vm.provision "shell", path: "./scripts/global.sh", env: common_env
    inventory.vm.provision "shell", path: "./scripts/inventory.sh", env: common_env
  end

  config.vm.define "billing-vm" do |billing|
    billing.vm.hostname = "billing-vm"
    billing.vm.network "private_network", ip: env.fetch("BILLING_VM_IP", "192.168.56.12")
    billing.vm.network "forwarded_port", guest: env.fetch("RABBITMQ_MANAGEMENT_PORT", "15672").to_i, host: env.fetch("RABBITMQ_MANAGEMENT_PORT", "15672").to_i
    billing.vm.synced_folder "./srcs/billing-app", "/home/vagrant/billing-app"

    billing.vm.provider "virtualbox" do |vb|
      vb.memory = 2048
      vb.cpus = 1
    end

    billing.vm.provision "shell", path: "./scripts/global.sh", env: common_env
    billing.vm.provision "shell", path: "./scripts/billing.sh", env: common_env
  end
end
