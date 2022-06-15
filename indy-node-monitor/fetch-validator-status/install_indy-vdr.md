# Instructions for local installation of indy-vdr

- Install Rust
```
sudo apt install build-essential rustc libssl-dev pkg-config cmake
```

- Clone the  indy-vdr repository
```
git clone https://github.com/hyperledger/indy-vdr
```

- Build
```
cd indy-vdr
cargo build --lib --release
```

- Copy indy-vdr library: 
```
sudo cp target/release/libindy*.so  /usr/local/lib
```

- Do ldconfig or export local libraries to library path
```
sudo ldconfig 
export LD_LIBRARY_PATH=/usr/local/lib
```
 
- Install the python wrapper (this can be done in a virtual environment):
```
cd Wrappers/Python
pip3 install .
```

- Install the python dependencies for fetch_status_prometheus.py:
```
pip3 install base58 pynacl
```
