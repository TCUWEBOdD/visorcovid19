#!/bin/bash
export PYTHONPATH=$PYTHONPATH:/home/odd/plataformacovid19
python3 /home/odd/plataformacovid19/flask_service/app.py > /home/odd/plataformacovid19/flask_service/service_log.txt 2>&1
