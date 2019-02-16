

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "generic/ubuntu1804"

  config.vm.define :lago1 do |box|
    box.vm.box = "generic/ubuntu1804"
    box.vm.hostname = "lago1"
    box.vm.network :private_network, ip: "192.168.55.11"
    box.vm.network :private_network, ip: "172.16.0.11", virtualbox__intnet: "lago-net-1"

    box.vm.provider "virtualbox" do |vb|
      vb.memory = "4096"
      vb.cpus = "4"
      vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
    end

    box.vm.provision "ansible" do |ansible|
      ansible.playbook = "provisioning/lago1.yml"
      ansible.inventory_path = "provisioning/hosts"
      ansible.limit = 'all'
    end
  end

  config.vm.define :lago2 do |box|
    box.vm.box = "generic/ubuntu1804"
    box.vm.hostname = "lago2"
    box.vm.network :private_network, ip: "192.168.55.12"
    box.vm.network :private_network, ip: "172.16.0.12", virtualbox__intnet: "lago-net-1"

    box.vm.provider "virtualbox" do |vb|
      vb.memory = "4096"
      vb.cpus = "4"
      vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
    end

    box.vm.provision "ansible" do |ansible|
      ansible.playbook = "provisioning/lago2.yml"
      ansible.inventory_path = "provisioning/hosts"
      ansible.limit = 'all'
    end
  end

end
