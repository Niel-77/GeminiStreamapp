# post_setup.sh
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:fenics-packages/fenics
sudo apt-get update
sudo apt-get install -y fenics
sudo apt-get dist-upgrade -y
