FROM dresscodeswift/heasoft:v6.28.swift

USER root

RUN \
    apt-get update && apt-get upgrade --yes \
    && apt-get install --yes --no-install-recommends \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER heasoft

ENV CALDB=/opt/heasoft/caldb
ENV WCSTOOL_VER=3.9.7
ENV PATH=/opt/heasoft/wcstools-$WCSTOOL_VER/bin:$PATH

RUN \
    # get/make wcstools
    wget --no-verbose tdc-www.harvard.edu/software/wcstools/wcstools-${WCSTOOL_VER}.tar.gz || wget --no-verbose tdc-www.harvard.edu/software/wcstools/Old/wcstools-${WCSTOOL_VER}.tar.gz \
    && tar -xf wcstools-${WCSTOOL_VER}.tar.gz -C /opt/heasoft \
    && rm wcstools-${WCSTOOL_VER}.tar.gz \
    && cd /opt/heasoft/wcstools-${WCSTOOL_VER} \
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
    && /bin/echo "source $CALDB/caldbinit.sh" >> /home/heasoft/.profile \
    && /bin/echo 'export CALDB='$CALDB >> /home/heasoft/.bashrc \
    && /bin/echo "source $CALDB/caldbinit.sh" >> /home/heasoft/.bashrc \
    && /bin/echo 'setenv CALDB '$CALDB >> /home/heasoft/.cshrc \
    && /bin/echo "source $CALDB/caldbinit.csh" >> /home/heasoft/.cshrc
