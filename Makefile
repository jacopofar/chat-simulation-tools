run:
	docker run --name chatlog-postgres -v pgdata:/var/lib/postgresql/data -p 5442:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres:11
	sleep 20 # maybe a better way to wait for the DB?
	docker exec chatlog-postgres sh -c "echo 'CREATE DATABASE clogs;' |psql -U postgres"
	python3 -m venv .venv
	.venv/bin/pip3 install -r requirements.txt
	.venv/bin/python3  process_tg_cli_logs.py
	.venv/bin/python3 logs_to_postgres.py
	.venv/bin/python3 chat_simulator/word_embeddings.py

