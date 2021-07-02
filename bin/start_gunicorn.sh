cd ~/vreports
source .venv/bin/activate
cd web
export PYTHONPATH='/home/dlink/vreports/lib:/home/dlink/vweb/src:/home/dlink/vlib/src'
gunicorn --reload wsgi:app
