deploy:
	docker-copose build && docker-compose up -d --force-recreate