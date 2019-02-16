

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "generic/ubuntu1804"

  config.vm.define :lagopus do |box|
    box.vm.box = "generic/ubuntu1804"
    box.vm.hostname = "lagopus"
    box.vm.network :private_network, ip: "192.168.55.11"
    box.vm.network :private_network, ip: "10.0.0.10", virtualbox__intnet: "lago-edge-1"
    box.vm.network :private_network, ip: "10.0.0.11", virtualbox__intnet: "lago-edge-2"

    box.vm.provider "virtualbox" do |vb|
      vb.memory = "4096"
      vb.cpus = "4"
      vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
      vb.customize ["modifyvm", :id, "--nicpromisc4", "allow-all"]
    end

    box.vm.provision "ansible" do |ansible|
      ansible.playbook = "provisioning/lagopus.yml"
      ansible.inventory_path = "provisioning/hosts"
      ansible.limit = 'all'
    end
  end

  config.vm.define :node1 do |box|
    box.vm.box = "generic/ubuntu1804"
    box.vm.hostname = "node1"
    box.vm.network :private_network, ip: "192.168.55.12"
    box.vm.network :private_network, ip: "10.0.0.20", virtualbox__intnet: "lago-edge-1"
    box.vm.network :private_network, ip: "10.0.0.21", virtualbox__intnet: "lago-edge-2"

    box.vm.provider "virtualbox" do |vb|
      vb.customize ["modifyvm", :id, "--nicpromisc2", "allow-all"]
      vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
    end

    box.vm.provision "ansible" do |ansible|
      ansible.playbook = "provisioning/node1.yml"
      ansible.inventory_path = "provisioning/hosts"
      ansible.limit = 'all'
    end
  end

end
