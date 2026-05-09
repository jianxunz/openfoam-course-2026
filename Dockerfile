FROM opencfd/openfoam-default:2512

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-numpy \
    python3-matplotlib \
    gnuplot \
    nano \
    vim \
    less \
    tree \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

COPY assignments/ /course/assignments/
COPY scripts/ /course/scripts/

RUN chmod +x /course/scripts/*.sh || true

CMD ["/bin/bash"]
