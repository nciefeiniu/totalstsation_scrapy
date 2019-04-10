#!/usr/bin/env bash

docker run -itd -p 8051:8050 -m 500m --memory-swap 500m --restart always scrapinghub/splash

docker run -itd -p 8052:8050 -m 500m --memory-swap 500m --restart always scrapinghub/splash

docker run -itd -p 8053:8050 -m 500m --memory-swap 500m --restart always scrapinghub/splash

docker run -itd -p 8054:8050 -m 500m --memory-swap 500m--restart always scrapinghub/splash


docker run -itd -p 8055:8050 -m 500m --memory-swap 500m --restart always scrapinghub/splash
