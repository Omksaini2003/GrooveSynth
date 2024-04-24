# GrooveSynth

![Prot1-image](./assets/prot1.jpg)

## About the repo

GrooveSynth is a tool that generates active sites pdb consisting of all the provided IDs of the amino acid from the parent protein chain.

## How to install 

1. Install from this repo as:

```
git clone https://github.com/Omksaini2003/groove.git
```

2. Create a virtual environment

```
python3 -m venv env 
source env/bin/activate
```

3.  To Run this flask app:

```
python3 app.py
```
   

## How to use

![Page1](./assets/page1.png)

1. Provide the input of the pdb file (eg:- 4dfr.pdb)
2. Enter the IDs of the amino acid (eg:- 1,2,5)
3. Enter the threshold of the Alanines you require (eg:- 1)
4. By clicking 'Process', you will be downloading the pdb file connecting all the active site amino acids.

## Requirements

1. <b> Packages </b> :

* Flask == 3.0.3
* Pip == 22.0.2
* python == 3.10.12

2. <b> OS Systems </b>:  It supports all OS systems (Windows, MACOS, and Linux).
