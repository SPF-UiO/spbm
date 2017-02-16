#!/bin/bash -e

echo "Backing up SPBM"

now=$(date -u +%Y%m%d_%H%M%S)Z
dumpfile=backup-$now.json
dumpfolder=../backups

#backupfile=internsystem_backup_$(hostname -s)_${ENV}_$now.tgz
#dest=cyb@login.ifi.uio.no:backups/$backupfile
#backupfile=/tmp/$backupfile

source .virtualenv/bin/activate
./manage.py dumpdata -o $dumpfolder/$dumpfile

#tar zcf $backupfile $sqlfile
#rm $sqlfile

# scp -o StrictHostKeyChecking=no $backupfile $dest

echo "Completed backup of SPBM data to $dumpfolder"



#ls -lh $backupfile
#rm $backupfile
