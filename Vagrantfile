# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "generic/ubuntu2004"

  config.vm.provider "virtualbox" do |v|
    v.gui = false
    v.name = "leaf-focus-box"
    v.check_guest_additions = true
    v.memory = 4096
    v.cpus = 6
  end

  # set auto_update to false, if you do NOT want to check the correct
  # additions version when booting this machine
  config.vbguest.auto_update = false

  # set no_remote to true if you do NOT want to download the iso file from a webserver
  config.vbguest.no_remote = true

  config.vm.synced_folder ".", "/opt/leaf-focus/source", type: "rsync", rsync__exclude: [".git/", ".github/", ".vagrant/", "__pycache__/"]

  data_dir = ENV["LEAF_FOCUS_DATA_DIR"]
  raise "Missing 'LEAF_FOCUS_DATA_DIR'" unless data_dir

  config.vm.synced_folder data_dir, "/mnt/data"

  config.vm.provision "install_ansible", type: "shell", inline: <<-SHELL
    if [ ! -f "/etc/apt/sources.list.d/deadsnakes-ubuntu-ppa-focal.list" ]; then
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install software-properties-common python3-apt python-apt-common python3-packaging apt-transport-https
      sudo DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:deadsnakes/ppa
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq update
    fi

    if [ ! -d "/opt/leaf-focus/ansible-venv" ]; then
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install python3.9 python3.9-dev python3.9-venv python3.9-distutils
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install libxml2-dev libxslt-dev zlib1g-dev libffi-dev
      sudo DEBIAN_FRONTEND=noninteractive apt-get -yq upgrade

      DEBIAN_FRONTEND=noninteractive python3.9 -m venv /opt/leaf-focus/ansible-venv
      echo 'PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/opt/leaf-focus/ansible-venv/bin"' | sudo tee /etc/environment > /dev/null
      source /opt/leaf-focus/ansible-venv/bin/activate

      /opt/leaf-focus/ansible-venv/bin/python -m pip install -U pip
      /opt/leaf-focus/ansible-venv/bin/pip install -U setuptools wheel
      /opt/leaf-focus/ansible-venv/bin/pip install -U lxml
      /opt/leaf-focus/ansible-venv/bin/pip install -U ansible
    fi

    if [ ! -d "/vagrant" ]; then
      sudo mkdir -p /vagrant
      sudo chown vagrant:vagrant /vagrant
    fi

  SHELL

  config.vm.provision "run_ansible", type: "ansible_local"  do |ansible|
    ansible.compatibility_mode = "2.0"
    ansible.config_file = "/opt/leaf-focus/source/ansible/ansible.cfg"
    ansible.playbook = "/opt/leaf-focus/source/ansible/playbook.yml"
    ansible.install = false
  end

  # redis
  config.vm.network "forwarded_port", guest: 6379, host: 6379
  config.vm.network "forwarded_port", guest: 8081, host: 8081

  # rabbitmq
  config.vm.network "forwarded_port", guest: 15672, host: 15672

  # celery flower
  config.vm.network "forwarded_port", guest: 5555, host: 5555

end
