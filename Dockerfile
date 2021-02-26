ARG PY_VER=3.8
ARG DISTRO=alpine
ARG IMAGE=djlab
FROM datajoint/${IMAGE}:py${PY_VER}-${DISTRO}
COPY --chown=dja:anaconda requirements.txt $PIP_REQUIREMENTS
RUN \
  echo "msttcorefonts-installer make texlive-full imagemagick git" | tr " " "\n" \
    > "${APK_REQUIREMENTS}" && \
  /entrypoint.sh echo "Requirements updated..." && \
  rm "$APK_REQUIREMENTS" && \
  rm "$PIP_REQUIREMENTS"
USER root
RUN update-ms-fonts
USER dja:anaconda
