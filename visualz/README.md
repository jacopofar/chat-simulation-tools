This is a very experimental app using aiohttp as a backend and react for
the frontend.

## Run it in development mode

Both the frontend and the backend support auto-reloading whenever something
 changes, so:

Run `make install-dev-backend` to create the virtualenv and install the
dependencies and the model there.

Then if you have tmux installed `make parallel-tmux-dev` will run the backend,
frontend and frontend tests together. It should also start the browser.

If you don't have tmux or prefer to start things manually:

Run `make run-dev-frontend` to start the frontend in dev mode.

Run `make run-dev-backend` to create the virtualenv and serve the backend.
