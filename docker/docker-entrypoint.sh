#!/bin/bash
python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files

# Prepare log files and start outputting logs to stdout
touch /srv/logs/gunicorn.log
touch /srv/logs/access.log
tail -n 0 -f /srv/logs/*.log &


echo Starting nginx.
systemctrl start nginx

# Start Gunicorn processes
NAME="PyScada_gunicorn"                           # Name of the application
DJANGODIR=`pwd`				          			            # Django project directory
SOCKFILE="$DJANGODIR/run/gunicorn.sock"   	      # we will communicte using this unix socket
USER=`whoami`                                     # the user to run as
GROUP=$(id -gn)                                   # the group to run as
NUM_WORKERS=5                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE="PyScadaServer.settings"              # which settings file should Django use
DJANGO_WSGI_MODULE="PyScadaServer.wsgi"                      # WSGI module name
PID_FILE="$DJANGODIR/run/gunicorn.pid"		  # name and path of the PID file



echo "Starting Gunicorn $NAME as $GROUP:`whoami`"
#echo $DJANGODIR
#echo $SOCKFILE
#echo $USER
#echo $DJANGO_SETTINGS_MODULE
#echo $DJANGO_WSGI_MODULE
#echo $GROUP

# Activate the virtual environment
#cd $DJANGODIR
#source ../bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
chown $USER:$USER $RUNDIR
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --log-level=info \
  --bind=unix:$SOCKFILE \
  --pid $PID_FILE
  --log-file=/srv/logs/gunicorn.log \
  --access-logfile=/srv/logs/access.log \
    "$@"
