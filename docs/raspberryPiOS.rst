Raspberry Pi OS Installation
============================

Download last Lite image from `here <https://www.raspberrypi.com/software/operating-systems/>`__

Copy the image on the SD card using (change the name of the zip file and the path to the sd card)::

    unzip -p the_zip_file.zip | sudo dd of=/dev/sdX bs=4M conv=fsync status=progress

    or

    xz -dc the_xz_file.xz | sudo dd of=/dev/sdX bs=4M conv=fsync status=progress

More informations `here <https://www.raspberrypi.com/documentation/computers/getting-started.html>`__
