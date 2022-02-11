Mysql
-----
Add user and give SELECT rights : sudo mysql -uroot -p -e "GRANT SELECT ON PyScada_db.* TO 'Grafana-user'@'localhost' IDENTIFIED BY 'Grafana-user-password';"

Nginx
-----
Add in /etc/nginx/nginx.conf after http { ... } :
::
 include /etc/nginx/grafana-access.conf;
Create /etc/nginx/grafana-access.conf with :
::
 stream {
     # MySQL server
     server {
         listen     3305;
         proxy_pass 127.0.0.1:3306;
         proxy_timeout 60s;
         proxy_connect_timeout 30s;
     }
 }
Restart Nginx : 
::
 sudo systemctl restart nginx

Grafana
-------
Add DB :
 - Host :
     - Local : /run/mysqld/mysqld.sock
     - Remote : remote_ip:3305
 - Database : PyScada_db
 - User : Grafana-user
 - Password : Grafana-user-password
Import the exported dashboard (json file in extras directory).
Or for example, add theses variables : set refresh on dashboard load, multi-value and all option :
 - Add mysql datasource variable (type Datasource).
 - Add variables with type query using $Datasource :
  - Protocols : SELECT protocol AS __text, id AS __value FROM pyscada_deviceprotocol
  - Devices : SELECT d.short_name AS __text, d.id AS __value FROM pyscada_device d WHERE d.protocol_id IN (${Protocols}) AND d.active = 1
  - Units : SELECT u.unit AS __text, u.id AS __value FROM pyscada_unit u
  - Variables : SELECT v.name AS __text, v.id AS __value FROM pyscada_variable v WHERE v.device_id IN (${Devices}) AND v.unit_id IN (${Units}) AND v.active = 1
  - Time group (type Interval) : 1s,10s,1m,10m,30m,1h,6h,12h,1d,7d,14d,30d,1M
  - Null as (type custom) : 0, NULL, previous

Example query :
::
 SELECT
   $__timeGroupAlias(r.date_saved,$time_group),
   avg(IFNULL(r.value_float64, 0.0) + IFNULL(r.value_int64, 0.0) + IFNULL(r.value_int32, 0.0) + IFNULL(r.value_int16, 0.0) + IFNULL(r.value_boolean, 0.0)),
   v.name AS metric
 FROM pyscada_recordeddata as r
 JOIN pyscada_variable v ON r.variable_id = v.id
 WHERE
   $__timeFilter(r.date_saved) AND
   r.variable_id IN (${Variables})
 GROUP BY time, metric
 ORDER BY $__timeGroup(r.date_saved,$time_group,$null_as)

Embed in pyscada HMI
--------------------
Edit Grafana config file:
::
 sudo nano /etc/grafana/grafana.ini
Find and set :
 - allow_embedding = true
 - For localhost grafana : root_url = http://localhost:3000/grafana/
For localhost grafana add in /etc/nginx/sites-enabled/pyscada.conf :
::
 location /grafana/ {
     proxy_pass http://127.0.0.1:3000/;
 }
Restart Grafana server:
::
 sudo systemctl restart grafana-server.service
Create a custom html panel with the code from a dashboard or a panel from sharing options in grafana

Other
-----
use ssl : http://www.turbogeek.co.uk/2020/09/30/grafana-how-to-configure-ssl-https-in-grafana/
