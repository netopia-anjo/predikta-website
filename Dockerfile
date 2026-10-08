FROM nginx:stable-alpine

ENV PORT=8080
ENV NGINX_ENVSUBST_FILTER=^PORT$

COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY ["Fortified Predikta Website.html", "/usr/share/nginx/html/index.html"]
COPY copy.json /usr/share/nginx/html/copy.json

EXPOSE 8080
