run:
	docker run --name chatlog-postgres -v tgpgdata:/var/lib/postgresql/data -p 5442:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres:12
	docker exec chatlog-postgres sh -c 'until pg_isready; do echo "Waiting for the DB to be up..."; sleep 2; done'
	docker exec chatlog-postgres sh -c "echo 'CREATE DATABASE clogs;' |psql -U postgres"
	python3 -m venv .venv
	.venv/bin/pip3 install -r requirements.txt
	# ingestion
	.venv/bin/python3 tweets_to_postgres.py
	.venv/bin/python3 process_tg_cli_logs.py
	.venv/bin/python3 logs_to_postgres.py

	# .venv/bin/python3 chat_to_markov.py

	# .venv/bin/python3 chat_simulator/word_embeddings.py
	# .venv/bin/python3 chat_simulator.py

tabula-rasa:
	docker kill chatlog-postgres || echo 'probably no container was there'
	docker rm chatlog-postgres || echo 'probably no container was there'
	docker volume rm tgpgdata || echo 'probably no volume was there'
