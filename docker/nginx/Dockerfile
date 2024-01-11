FROM nginx:latest

LABEL maintainer="PyScada | Martin Schröder <info@martin-schroeder.net"

COPY nginx.conf /etc/nginx/
COPY ssl/pyscada_server.crt /etc/nginx/ssl/
COPY ssl/pyscada_server.key /etc/nginx/ssl/
#RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled
EXPOSE 80
EXPOSE 443
CMD ["nginx", "-g", "daemon off;"]
