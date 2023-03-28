# nbcheck: tools for checking notebooks

The tools contained in this repository are being developed as part of the GMLC-DISPATCHES project. Unless explicitly noted, their usage is bound to the same copyrights, license, etc as specificed in the main DISPATCHES repository at https://github.com/gmlc-dispatches/dispatches.

## Quickstart

### Installation

```sh
# install from 0.2.0 tag
pip install "git+https://github.com/gmlc-dispatches/nbcheck@0.2.0"

# install from current `main` branch
pip install "git+https://github.com/gmlc-dispatches/nbcheck@main"

# install from commit whose SHA starts with `abcd123`
pip install "git+https://github.com/gmlc-dispatches/nbcheck@abcd123"
```

### Usage

```sh
# run nbcheck with static checks only
pyest --nbcheck=static

# run nbcheck with both static and exec checks
pytest --nbcheck=static --nbcheck=exec

# disable the built-in `python` plugin to only run test items created by nbcheck
pytest --nbcheck=static --nbcheck=exec -p no:python
```
