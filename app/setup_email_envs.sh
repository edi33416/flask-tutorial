# Test local server with
# python -m smtpd -n -c DebuggingServer localhost:8025

export MAIL_SERVER=localhost
export MAIL_PORT=8025
#export MAIL_USE_TLS=0
#export MAIL_USERNAME=<your-gmail-username>
#export MAIL_PASSWORD=<your-gmail-password>

#export MAIL_SERVER=smtp.googlemail.com
#export MAIL_PORT=587
#export MAIL_USE_TLS=1
#export MAIL_USERNAME=<your-gmail-username>
#export MAIL_PASSWORD=<your-gmail-password>

# sql_alchemy_conn = postgresql+psycopg2://$your_db_user:$your_db_password@$your_postgres_db_host:$postgres_port/$db_name
export DATABASE_URL=postgresql+psycopg2://cadmus:cadmus@localhost:5432/cadmus
