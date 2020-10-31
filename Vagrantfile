# zcu-kiv-ds-1

Vagrant.configure("2") do |config|

  config.vm.box = "debian/buster64"
  config.vm.synced_folder ".", "/vagrant"

  (1..4).each do |i|
    config.vm.define "bank-server-#{i}" do |node|
      node.vm.hostname = "bank-server-#{i}"
      node.vm.network "private_network", ip: "192.168.151.#{30 + i}"
      node.vm.provision "shell", inline: <<~SHELL
        apt-get update
        apt-get -y install python3-waitress python3-flask
        mkdir -p /opt/zcu-kiv-ds-1
        cp /vagrant/src/bank_server.py /vagrant/src/error_handlers.py /opt/zcu-kiv-ds-1/
        cp /vagrant/unit/bank-server.service /etc/systemd/system/
        systemctl --now enable bank-server
      SHELL
    end
  end

  config.vm.define "shuffler" do |node|
    node.vm.hostname = "shuffler"
    node.vm.network "private_network", ip: "192.168.151.20"
    node.vm.provision "shell", inline: <<~SHELL
      apt-get update
      apt-get -y install python3-waitress python3-flask python3-requests
      mkdir -p /opt/zcu-kiv-ds-1
      cp /vagrant/src/shuffler.py /vagrant/src/error_handlers.py /opt/zcu-kiv-ds-1/
      cp /vagrant/unit/shuffler.service /etc/systemd/system/
      systemctl --now enable shuffler
    SHELL
  end

  config.vm.define "sequencer" do |node|
    node.vm.hostname = "sequencer"
    node.vm.network "private_network", ip: "192.168.151.10"
    node.vm.provision "shell", inline: <<~SHELL
      apt-get update
      apt-get -y install python3-waitress python3-flask python3-requests
      mkdir -p /opt/zcu-kiv-ds-1
      cp /vagrant/src/sequencer.py /vagrant/src/error_handlers.py /opt/zcu-kiv-ds-1/
      cp /vagrant/unit/sequencer.service /etc/systemd/system/
      systemctl --now enable sequencer
    SHELL
  end

end
