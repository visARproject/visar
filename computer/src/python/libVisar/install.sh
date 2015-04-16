sudo apt-get install gcc automake autoconf libtool bison swig python-dev libpulse-dev libspeex-dev libasound2-dev
sudo apt-get install python-numpy python-qt4 python-opengl python-scipy
sudo apt-get install python-pip
sudo pip install PyOpenGL

OLD_DIR=$PWD

mkdir -p ~/repos
cd ~/repos
git clone https://github.com/cmusphinx/sphinxbase
cd sphinxbase
./autogen.sh
make
sudo make install
cd ..

git clone https://github.com/cmusphinx/pocketsphinx
cd pocketsphinx
./autogen.sh
make
sudo make install
cd ..

git clone git@github.com:vispy/vispy.git
cd vispy
git checkout b64489b

echo "export LD_LIBRARY_PATH=/usr/local/lib" >> ~/.bashrc
echo "export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig" >> ~/.bashrc
source ~/.bashrc
cd $OLD_DIR