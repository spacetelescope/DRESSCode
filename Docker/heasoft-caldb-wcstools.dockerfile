FROM dresscodeswift/heasoft:v6.28.swift

USER root

RUN \
    apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install \
    python3-pip \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER heasoft

ENV CALDB=/opt/heasoft/caldb \
    PATH=/opt/heasoft/wcstools-3.9.6/bin:$PATH

RUN \
    # get wcstools
    wget tdc-www.harvard.edu/software/wcstools/wcstools-3.9.6.tar.gz \
    && tar -xf wcstools-3.9.6.tar.gz -C /opt/heasoft \
    && rm wcstools-3.9.6.tar.gz \
    && cd /opt/heasoft/wcstools-3.9.6 \
    && make all \
    && cd $CALDB \
    && wget https://heasarc.gsfc.nasa.gov/FTP/caldb/data/swift/uvota/goodfiles_swift_uvota.tar.Z \
    && tar -zxf goodfiles_swift_uvota.tar.Z \
    && rm goodfiles_swift_uvota.tar.Z \
    && /bin/echo 'export CALDB='$CALDB >> /home/heasoft/.profile \
    && /bin/echo 'export CALDB='$CALDB >> /home/heasoft/.bashrc \
    && /bin/echo 'setenv CALDB '$CALDB >> /home/heasoft/.cshrc
