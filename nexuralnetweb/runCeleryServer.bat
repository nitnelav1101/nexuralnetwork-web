SET FLASK_APP=nexuralnetweb
python -m celery -A %FLASK_APP%.celery worker --loglevel=info
