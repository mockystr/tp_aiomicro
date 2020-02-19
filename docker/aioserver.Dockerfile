FROM mockystr/docker-tp-aiomicro-base

EXPOSE 8080
CMD ["./scripts/aioserver_setup.sh"]
