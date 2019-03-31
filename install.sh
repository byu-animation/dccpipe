#if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
#    echo 'export PATH=$HOME/.local/bin:$PATH' >> $HOME/.bashrc
#		source $HOME/.bashrc
#fi

export PATH=$HOME/.local/bin:$PATH

python3 install.py
