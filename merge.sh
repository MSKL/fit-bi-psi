#!/bin/bash

cat includes.inc > whole_app.py

cat ./*.py ./classes/*.py | grep -Ev "import" >> whole_app.py