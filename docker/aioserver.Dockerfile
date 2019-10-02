FROM docker_skill-base

EXPOSE 8080
CMD ["./scripts/aioserver_setup.sh"]
