echo "#!/bin/bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt" > setup_env.sh
chmod +x setup_env.sh