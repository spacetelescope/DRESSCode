FROM dresscodeswift/heasoft:v6.28.swift

USER root

RUN \
    apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER heasoft

ENV CALDB=/opt/heasoft/caldb \
    PATH=/opt/heasoft/wcstools-3.9.7/bin:$PATH

RUN \
    # get/make wcstools
    wget --no-verbose tdc-www.harvard.edu/software/wcstools/wcstools-3.9.7.tar.gz \
    && tar -xf wcstools-3.9.7.tar.gz -C /opt/heasoft \
    && rm wcstools-3.9.7.tar.gz \
    && cd /opt/heasoft/wcstools-3.9.7 \
    && make all \
    # get caldb
    && cd $CALDB \
    && wget --no-verbose https://heasarc.gsfc.nasa.gov/FTP/caldb/software/tools/caldb_setup_files.tar.Z \
    && tar -zxvf caldb_setup_files.tar.Z \
    && rm caldb_setup_files.tar.Z \
    && wget --no-verbose https://heasarc.gsfc.nasa.gov/FTP/caldb/data/swift/uvota/goodfiles_swift_uvota.tar.Z \
    && tar -zxf goodfiles_swift_uvota.tar.Z \
    && rm goodfiles_swift_uvota.tar.Z \
    && caldbinfo INST swift uvota \
    && /bin/echo 'export CALDB='$CALDB >> /home/heasoft/.profile \
    && /bin/echo "source $CALDB/software/tools/caldbinit.sh" >> /home/heasoft/.profile \
    && /bin/echo 'export CALDB='$CALDB >> /home/heasoft/.bashrc \
    && /bin/echo "source $CALDB/software/tools/caldbinit.sh" >> /home/heasoft/.bashrc \
    && /bin/echo 'setenv CALDB '$CALDB >> /home/heasoft/.cshrc \
    && /bin/echo "source $CALDB/software/tools/caldbinit.csh" >> /home/heasoft/.cshrc
