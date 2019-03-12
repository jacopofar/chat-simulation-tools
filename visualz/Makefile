.PHONY: run-dev-backend \
		develop-frontend \
		build-frontend \
		install-dev-backend \
		test-frontend \
		parallel-tmux-dev

install-dev-backend: visualz/requirements.txt
	python3 -m venv .venv
	.venv/bin/python3 -m pip install -r visualz/requirements.txt
	# model for Italian, use whatever you need
	.venv/bin/python3 -m spacy download it

build-frontend:
	cd frontend && yarn build

run-dev-frontend:
	cd frontend && yarn start

run-dev-backend: install-dev-backend
	.venv/bin/adev runserver visualz

test-frontend:
	cd frontend && npm run test

parallel-tmux-dev:
	tmux new-session -d 'make run-dev-backend'
	tmux split-window -h 'make run-dev-frontend'
	tmux split-window -v 'make test-frontend'
	tmux -2 attach-session -d
