# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "generic/ubuntu2004"

  config.vm.provider "virtualbox" do |v|
    v.gui = false
    v.name = "leaf-focus-box"
    v.check_guest_additions = true
    v.memory = 2048
    v.cpus = 6
  end

  config.vm.synced_folder ".", "/opt/leaf-focus/source", type: "rsync", rsync__exclude: [".git/", ".github/", ".vagrant/"]

  config.vm.provision "install_ansible", type: "shell", inline: <<-SHELL
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq update
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install software-properties-common python3-apt python-apt-common python3-packaging
      sudo DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:ansible/ansible-4
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install ansible
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq upgrade
      sudo mkdir /vagrant
      sudo chown vagrant:vagrant /vagrant
  SHELL

  config.vm.provision "run_ansible", type: "ansible_local"  do |ansible|
    ansible.config_file = "/opt/leaf-focus/source/ansible/ansible.cfg"
    ansible.playbook = "/opt/leaf-focus/source/ansible/playbook.yml"
  end

  # elasticsearch
  config.vm.network "forwarded_port", guest: 9200, host: 9200
  config.vm.network "forwarded_port", guest: 9300, host: 9300
  config.vm.network "forwarded_port", guest: 5601, host: 5601
  # rabbitmq
  config.vm.network "forwarded_port", guest: 15672, host: 15672
  # celery flower
  config.vm.network "forwarded_port", guest: 5555, host: 5555
end
