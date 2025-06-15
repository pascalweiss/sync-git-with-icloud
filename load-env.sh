#!/bin/bash

# Load environment variables for sourcing (strips export prefix)
set -a
source <(sed 's/^export //' .env)
set +a

# Execute the passed command
exec "$@"
