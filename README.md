KindleButler
============

**KindleButler** is simple one click uploader that can transport MOBI/AZW3/AZW files to Kindle over USB or SSH.
Additionally it automatically handle all problems with covers and *Personal* tag on newer Kindle models.

## BINARY RELEASES
Latest **Windows** binaries are available [here](https://github.com/AcidWeb/KindleButler/releases).

## USAGE
On **Windows** just right click MOBI/AZW3/AZW file. All options should be there. If not - change file association.

Support of other OS is experimental. **KindleButler** should work but extensive testing was not performed.
There is no binary releases for **Linux/OSX**.

## USAGE - SSH
To upload book over Wi-Fi Kindle needs to be jailbroken and have fully configured USBNet hack.
User should be able to login using RSA key. Additionally **KindleButler** config file must be edited.

**Windows:** *KindleButler.ini* in program directory.

**Linux/OSX:** *~/.KindleButler*

### DEPENDENCIES:
- Python 3.3+
- [Pillow](http://pypi.python.org/pypi/Pillow/)
- [Psutil](https://pypi.python.org/pypi/psutil)
- [Paramiko](https://pypi.python.org/pypi/paramiko/)

## CHANGELOG
####0.1
* Initial release

## COPYRIGHT
Copyright (c) 2014 Pawel Jastrzebski
**KindleButler** is released under GNU General Public License. See LICENSE.txt for further details.

The application relies and includes the following scripts:
 - `DualMetaFix` script by **K. Hendricks**. Released with GPL-3 License.
 - `KindleUnpack` script by **M. Hannum, P. Durrant, K. Hendricks, S. Siebert, fandrieu, DiapDealer, nickredding**. Released with GPL-3 License.