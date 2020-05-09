# HCrawler

This is a simple python script to crawl through instagram's following
posts and stories. It will get post json and queue it into a queue.

It uses mainly `bot.api` calls, so I can have more control of how often I
make request. Using `bot` function would yield the facebook's usage
limit quite often and `bot` doesn't let you get the json string 
directly.

All api calls wait for `sleep_a_little`

## Environments variables

* `USERNAME`: instagram's username
* `PASSWORD`: instagram's password
* `RABBIT_HOST`: rabbitmq host name
* `CHANNELS`: a comma separated list of channels which this script will
publish to

E.g.
```bash
docker run -d \
	--name hcrawler \
	-e USERNAME="<username>" \
	-e PASSWORD="<password>" \
	-e RABBIT_HOST="localhost" \
	-e CHANNELS="instagram,backup" \
	registry.gitlab.com/gabrielgio/hcrawler:latest
```