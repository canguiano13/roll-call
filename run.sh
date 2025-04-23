
if [[ -z "${FLASK_DEBUG}" ]]; then
    echo "ENABLED FLASK DEBUGGING";
    export FLASK_DEBUG=1;
else 
    echo "";
fi

./.venv/bin/python -m flask run --host=0.0.0.0 --port=8080