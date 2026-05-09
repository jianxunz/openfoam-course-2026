FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-lc"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    software-properties-common \
    gpg \
    && wget -O - https://dl.openfoam.org/gpg.key > /etc/apt/trusted.gpg.d/openfoam.asc \
    && add-apt-repository -y http://dl.openfoam.org/ubuntu \
    && apt-get update \
    && apt-get install -y --no-install-recommends openfoam13 \
    && rm -rf /var/lib/apt/lists/*

# Avoid loading OpenFOAM bash-completion in non-interactive scripts
RUN cp /opt/openfoam13/etc/bashrc /opt/openfoam13/etc/bashrc.original && \
    sed -i 's|\[ "$BASH" \] && \. $WM_PROJECT_DIR/etc/config.sh/bash_completion|case "$-" in *i*) [ "$BASH" ] \&\& . $WM_PROJECT_DIR/etc/config.sh/bash_completion ;; esac|' \
    /opt/openfoam13/etc/bashrc

# Source OpenFOAM automatically for interactive Docker shells
RUN cat <<'EOF' >> /root/.bashrc

# OpenFOAM 13 environment
if [ -f /opt/openfoam13/etc/bashrc ] && [ -z "${WM_PROJECT_VERSION:-}" ]; then
    . /opt/openfoam13/etc/bashrc
fi
EOF

WORKDIR /work

COPY assignments/ /course/assignments/
COPY scripts/ /course/scripts/

RUN chmod +x /course/scripts/*.sh || true

CMD ["/bin/bash"]
