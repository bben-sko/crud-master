# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|


  
  config.vm.box = "bento/ubuntu-22.04"

  
  # config.vm.box_check_update = false

 
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # config.vm.network "private_network", ip: "192.168.33.10"

  # config.vm.network "public_network"

  # config.vm.synced_folder "../data", "/vagrant_data"

  # config.vm.synced_folder ".", "/vagrant", disabled: true

config.vm.define "gateway-vm" do |aga|
  aga.vm.network "private_network", ip: "192.168.56.1"
  aga.vm.hostname = "gateway-vm"
  aga.vm.synced_folder "./srcs/api-gateway-app" , "/home/vagrant/api-gateway-app"
     aga.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus   = 1
    end
aga.vm.provision "shell", path: "./scripts/global.sh"

end
config.vm.define "inventory-vm" do |ia|
    ia.vm.hostname = "inventory-vm"
    ia.vm.network "private_network", ip: "192.168.56.2"
    ia.vm.synced_folder "./srcs/inventory-app" , "/home/vagrant/inventory-app"
     ia.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus   = 1
end
ia.vm.provision "shell", path: "./scripts/global.sh"
end
config.vm.define "billing-vm" do |ba|
  ba.vm.hostname = "billing-vm"
  ba.vm.network "private_network", ip: "192.168.56.3"
  ba.vm.synced_folder "./srcs/billing-app" , "/home/vagrant/billing-app"
   ba.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus   = 1
    end
    ba.vm.provision "shell", path: "./scripts/global.sh"
end

 
  
  
end
