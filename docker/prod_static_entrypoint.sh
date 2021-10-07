#!/bin/bash

set -e

# Always keep this here as it ensures the built and digested assets get copied
# into the correct location. This avoids them getting clobbered by any volumes.
cp -r  /code/static /volumes

exec "$@"
