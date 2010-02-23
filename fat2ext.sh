#!/bin/bash

# fat2ext.sh - version 1.0 - 2003-11-16
# Created by Denilson F. de Sa
# 
# This thing fix the permissions after you copy anything
# from a FAT partition to a ext2/ext3 one.
# 
# This version is recursive and verbose. It changes all
# files to 644 and all directories to 755.
# 
# This script calls itself recursively to go deeper inside
# directory tree.
# 
# There are no option parameters. All parameters are
# considered as directories.
# 
# This script is very verbose, it tells you ALL changes that
# are made. Pipe it to a LOGFILE to see if everything is OK,
# or to /dev/null if you dare! :) I'm not responsible if
# anything goes wrong!


FILES=644
DIRS=755


if [ "$1" == "" ]; then
	echo "Please use:
  $0 .
To run this on current directory."

fi

PODEIR=0

echo RUNNED AS "$*"

while [ "$1" != "" ]; do
	cd "$1" && PODEIR=1
	pwd

	if [ $PODEIR == 1 ]; then
		chmod -v $FILES *
		ls -1F --color=no | sed -n 's/\/$//p' | xargs -iAAA chmod -v $DIRS AAA
		ls -1F --color=no | sed -n 's/\/$//p' | xargs -iAAA "$0" AAA
	fi
	PODEIR=0
	shift
done





# OLD VERSION
#ls -1F --color=no | sed -n 's/\*$//p' | xargs -iAAA chmod -x -v AAA
#Isto remove as permissões APENAS de arquivos. Em outras palavras, isto tira a permissão de executável de todos os executáveis.


#ls -1F --color=no | sed -n 's/\/$//p' | xargs -iAAA find AAA | egrep '[^/]/[^/]' | xargs -iBBB chmod -v -x BBB
#Isto remove as permissões de executável de todos os arquivos que estejam em apenas um nível abaixo do diretório atual.

#Depois eu crio uma solução melhor, mais genérica, mais bem feita e mais funcional.
