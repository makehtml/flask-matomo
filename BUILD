#!/bin/bash
# needed: pip install twine

# Create source distribution
python setup.py sdist

# Upload package
twine upload dist/*

# Clean dist/
rm -rf dist/*
rm -rf Flask_Matomo_D.egg-info/*