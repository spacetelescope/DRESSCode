FROM dresscodeswift/heasoft:v6.28.swift

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
