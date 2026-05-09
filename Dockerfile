FROM opencfd/openfoam-default:2512

USER root

WORKDIR /work

COPY assignments/ /course/assignments/
COPY scripts/ /course/scripts/

RUN chmod +x /course/scripts/*.sh || true

CMD ["/bin/bash"]
