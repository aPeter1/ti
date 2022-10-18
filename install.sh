#!/bin/sh

mkdir -p ~/bin
cp ti ~/bin
echo 'export PATH=$PATH":$HOME/bin"' >> ~/.profile
source ~/.profile