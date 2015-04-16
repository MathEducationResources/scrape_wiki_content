# Fixes single question
python wiki2json.py --q_filter=$1
python raw2latex.py --q_filter=$1
