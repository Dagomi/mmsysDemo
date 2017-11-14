#!/bin/bash
# Instalador Gstreamer 1.6.3
#echo -e "+-----------------------+\n Escribe contrasena Root \n+-----------------------+"
mkdir ~/temp/
cd temp/
sudo apt-get -y install libxv1 libxv-dev libxvidcore4 libxvidcore-dev faac faad libfaac-dev libfaad-dev bison libavl-dev yasm flex zlib1g-dev libffi-dev gettext
#echo -e "+-----------------------+\n  Creada carpeta Temp \n+-----------------------+"
# Glib 2.48 
wget http://ftp.gnome.org/pub/gnome/sources/glib/2.48/glib-2.48.0.tar.xz
tar -xf glib-2.48.0.tar.xz
cd glib-2.48.0
./configure --prefix=/usr
make
sudo make install
cd ~/temp
#echo -e "+-----------------------+\n  Glib 2.48  Instalado \n+-----------------------+"

#Dependencias adicionales
sudo apt-get -y install libasound2-dev libgudev-1.0-dev libxt-dev libvorbis-dev libcdparanoia-dev libpango1.0-dev libtheora-dev libvisual-0.4-dev iso-codes libgtk-3-dev libraw1394-dev libiec61883-dev libavc1394-dev libv4l-dev libcairo2-dev libcaca-dev libspeex-dev libpng-dev libshout3-dev libjpeg-dev libaa1-dev libflac-dev libdv4-dev libtag1-dev libwavpack-dev libpulse-dev libsoup2.4-dev libbz2-dev libcdaudio-dev libdc1394-22-dev ladspa-sdk libass-dev libcurl4-gnutls-dev libdca-dev libdirac-dev libdvdnav-dev libexempi-dev libexif-dev libfaad-dev libgme-dev libgsm1-dev libiptcdata0-dev libkate-dev libmimic-dev libmms-dev libmodplug-dev libmpcdec-dev libofa0-dev librsvg2-dev librtmp-dev libschroedinger-dev libslv2-dev libsndfile1-dev libsoundtouch-dev libspandsp-dev libx11-dev libxvidcore-dev libzbar-dev libzvbi-dev liba52-0.7.4-dev libcdio-dev libdvdread-dev libmad0-dev libmp3lame-dev libmpeg2-4-dev libopencore-amrnb-dev libopencore-amrwb-dev libsidplay1-dev libtwolame-dev libx264-dev


#Kernel Gstreamer 1.6.3

wget https://gstreamer.freedesktop.org/src/gstreamer/gstreamer-1.8.3.tar.xz
tar -xf gstreamer-1.8.3.tar.xz
cd gstreamer-1.8.3
./configure --prefix=/usr
make 
sudo make install
cd ~/temp
#echo -e "+-----------------------+\n  Kernel Gstreamer 1.6.3 ok \n+-----------------------+"


# Instalación de códecs y componentes adicionales

sudo apt-get -y install libtheora-dev libogg-dev libvorbis-dev libasound2-dev libjack-dev

# Instalación de libvisual
sudo apt-get -y install libxv-dev libvisual-0.4-dev

# Instalacion de componentes “Autotools”
sudo apt-get install -y bison git-core autoconf pkg-config libtool autopoint gtk-doc-tools flex libogg-dev libtheora-dev libvorbis-dev libpango1.0-dev libasound2-dev libcdparanoia-dev libspeex-dev libjpeg-dev libwavpack-dev libopus-dev librtmp-dev libx264-dev yasm
echo "<-- libvisual y Autotools  Instalados -->" 

# Instalación de los Base Plugins Gstreamer

wget https://gstreamer.freedesktop.org/src/gst-plugins-base/gst-plugins-base-1.8.3.tar.xz
tar -xf gst-plugins-base-1.8.3.tar.xz
cd gst-plugins-base-1.8.3
./autogen.sh 
./configure --prefix=/usr
make
sudo make install
cd ~/temp

#echo -e "+-----------------------+\n  Base Plugins 1.6.3 ok \n+-----------------------+"


# Instalación de los Good Plugins Gstreamer

wget https://gstreamer.freedesktop.org/src/gst-plugins-good/gst-plugins-good-1.8.3.tar.xz
tar -xf gst-plugins-good-1.8.3.tar.xz
cd gst-plugins-good-1.8.3
./autogen.sh 
./configure --prefix=/usr
make
sudo make install
cd ~/temp

#echo -e "+-----------------------+\n  Good Plugins 1.6.3 ok \n+-----------------------+"

# Instalación de los Bad Plugins Gstreamer

wget https://gstreamer.freedesktop.org/src/gst-plugins-bad/gst-plugins-bad-1.8.3.tar.xz
tar -xf gst-plugins-bad-1.8.3.tar.xz
cd gst-plugins-bad-1.8.3
./autogen.sh 
./configure --prefix=/usr
make
sudo make install
cd ~/temp

#echo -e "+-----------------------+\n  Bad Plugins 1.6.3 ok \n+-----------------------+"

# Instalación Libav

wget https://gstreamer.freedesktop.org/src/gst-libav/gst-libav-1.8.3.tar.xz
tar -xf gst-libav-1.8.3.tar.xz
cd gst-libav-1.8.3
./autogen.sh 
./configure --prefix=/usr
make
sudo make install
cd ~/temp

#echo -e "+-----------------------+\n  Libav Plugins 1.6.3 ok \n+-----------------------+\n"

# Instalación Python Gstreamer

wget https://gstreamer.freedesktop.org/src/gst-python/gst-python-1.8.2.tar.xz
tar -xf gst-python-1.8.2.tar.xz
cd gst-python-1.8.2
./autogen.sh 
./configure --prefix=/usr
make
sudo make install
cd ~/temp

#echo -e "+-----------------------+\n   Python Gstreamer 1.6.3 ok \n+-----------------------+\n"


