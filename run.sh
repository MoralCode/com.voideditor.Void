#!/bin/bash -xv
export ZYPAK_APP_IMAGE_PATH=/app
export ZYPAK_APP_PATH=/app/

function errmsg() {
  >&2 echo "flatpak-cursor: $*"
}

# Activate any enabled SDK extensions
if [[ "$FLATPAK_ENABLE_SDK_EXT" == "*" ]]; then
  SDK=()
  for d in /usr/lib/sdk/*; do
    SDK+=("${d##*/}")
  done
else
  IFS=',' read -ra SDK <<<"$FLATPAK_ENABLE_SDK_EXT"
fi

for i in "${SDK[@]}"; do
  if [[ -d /usr/lib/sdk/$i ]]; then
    errmsg "Enabling SDK extension \"$i\""
    if [[ -f "/usr/lib/sdk/$i/enable.sh" ]]; then
      . "/usr/lib/sdk/${i}/enable.sh"
    else
      export PATH=$PATH:/usr/lib/sdk/$i/bin
    fi
  else
    errmsg "Requested SDK extension \"$i\" is not installed"
  fi
done

exec /app/bin/zypak-wrapper /app/bin/void "$@"
