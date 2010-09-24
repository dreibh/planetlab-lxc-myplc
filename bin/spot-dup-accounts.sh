#!/bin/bash

DB=planetlab5
USER=pgsqluser
CMD="select email, count(email) from persons where deleted=false group by email having count(email) > 2;"

psql -U $USER $DB -c "$CMD"
