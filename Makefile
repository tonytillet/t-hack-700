.PHONY: start dev stop logs

dev:
	docker compose -f compose.yml -f compose.dev.yml up --build

start:
	docker compose up --build

stop:
	docker compose down

logs:
	docker compose logs -f
