FROM node:16

RUN mkdir -p /www/website

ADD ./package.json /www/website/

ADD ./yarn.lock /www/website/

RUN yarn

WORKDIR /www/website

EXPOSE 3000
