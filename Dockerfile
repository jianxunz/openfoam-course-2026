FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/pyenv/bin:$PATH"
ENV MPLBACKEND=Agg
ENV PYTHONUNBUFFERED=1

SHELL ["/bin/bash", "-lc"]

# ============================================================
# Install OpenFOAM Foundation v13 and Python environment
# ============================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    software-properties-common \
    gpg \
    bash \
    nano \
    vim \
    less \
    tree \
    git \
    python3 \
    python3-venv \
    python3-pip \
    && wget -O - https://dl.openfoam.org/gpg.key > /etc/apt/trusted.gpg.d/openfoam.asc \
    && add-apt-repository -y http://dl.openfoam.org/ubuntu \
    && apt-get update \
    && apt-get install -y --no-install-recommends openfoam13 \
    && python3 -m venv /opt/pyenv \
    && /opt/pyenv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel \
    && /opt/pyenv/bin/pip install --no-cache-dir numpy matplotlib scipy \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# Make python, python3, pip and pip3 point to the virtual environment
# This ensures that "python3 plot.py" can import numpy, matplotlib and scipy.
# ============================================================

RUN ln -sf /opt/pyenv/bin/python /usr/local/bin/python && \
    ln -sf /opt/pyenv/bin/python3 /usr/local/bin/python3 && \
    ln -sf /opt/pyenv/bin/pip /usr/local/bin/pip && \
    ln -sf /opt/pyenv/bin/pip3 /usr/local/bin/pip3

# ============================================================
# Avoid OpenFOAM bash-completion issue in non-interactive scripts
# ============================================================

RUN cp /opt/openfoam13/etc/bashrc /opt/openfoam13/etc/bashrc.original && \
    sed -i 's|\[ "$BASH" \] && \. $WM_PROJECT_DIR/etc/config.sh/bash_completion|case "$-" in *i*) [ "$BASH" ] \&\& . $WM_PROJECT_DIR/etc/config.sh/bash_completion ;; esac|' \
    /opt/openfoam13/etc/bashrc

# ============================================================
# Source OpenFOAM and Python environment automatically
# ============================================================

RUN cat <<'EOF' >> /etc/bash.bashrc

# OpenFOAM 13 environment
if [ -f /opt/openfoam13/etc/bashrc ] && [ -z "${WM_PROJECT_VERSION:-}" ]; then
    source /opt/openfoam13/etc/bashrc
fi

# Python virtual environment
export PATH="/opt/pyenv/bin:$PATH"
EOF

RUN cat <<'EOF' >> /root/.bashrc

# OpenFOAM 13 environment
if [ -f /opt/openfoam13/etc/bashrc ] && [ -z "${WM_PROJECT_VERSION:-}" ]; then
    source /opt/openfoam13/etc/bashrc
fi

# Python virtual environment
export PATH="/opt/pyenv/bin:$PATH"
EOF

# ============================================================
# Course working directory
# ============================================================

WORKDIR /work

COPY assignments/ /course/assignments/
COPY scripts/ /course/scripts/

RUN chmod -R +x /course/scripts || true && \
    chmod -R a+rX /course && \
    chmod -R a+rX /opt/pyenv

CMD ["/bin/bash"]
