#!/bin/bash
usage() { echo "make-icon: [-n NICKNAME] projectName projectDir" 1>&2; exit; }

nickname=""

while getopts n: option
do
	case "${option}"
	in
		n) nickname=${OPTARG}
		shift
		shift
		;;
		*)
		usage
	esac
done

if [ "$1" == "" ]||[ "$2" == "" ]; then
	usage
fi

PROJECT_NAME="$1"
PROJECT_PATH="$2"

function icon {
	icon_usage() { echo "icon: [-n NICKNAME] projectName projectDir scriptName scriptIcon script" 1>&2; exit; }
	local nickname=""

	local OPTIND n option
	while getopts ":n:" option
	do
		case "${option}"
		in
			n) nickname=${OPTARG}
			shift
			shift
			;;
		esac
	done

	if [ "$1" == "" ]||[ "$2" == "" ]||[ "$3" == "" ]||[ "$4" == "" ]||[ "$5" == "" ]; then
		icon_usage
	fi

	PROJECT_NAME="$1"
	PROJECT_PATH="$2"
	SOFTWARE_NAME="$3"
	ICON="$4"
	SCRIPT="$5"

	if [ "$nickname" == "" ]; then
		PROGRAM_NAME=${PROJECT_NAME}" "${SOFTWARE_NAME}
	else
		PROGRAM_NAME=$nickname
	fi

	NOSPACES=${SOFTWARE_NAME// /-}
	FILENAME=${PROJECT_PATH}"/dcc_${NOSPACES,,}"

	echo "#!/usr/bin/env xdg-open" > ${FILENAME}.desktop
	echo "[Desktop Entry]" >> ${FILENAME}.desktop
	echo "Version=0.1" >> ${FILENAME}.desktop
	echo "Name=${PROGRAM_NAME}" >> ${FILENAME}.desktop
	echo "Name[en_US]=${PROGRAM_NAME}" >> ${FILENAME}.desktop
	echo "Comment=DCC Pipe shortcut for ${SOFTWARE_NAME}" >> ${FILENAME}.desktop
	echo "Exec=${PROJECT_PATH}/${SCRIPT}" >> ${FILENAME}.desktop
	echo "Icon=${PROJECT_PATH}/${ICON}" >> ${FILENAME}.desktop
	echo "Terminal=false" >> ${FILENAME}.desktop
	echo "Type=Application" >> ${FILENAME}.desktop
	echo "Categories=Utility;Application;" >> ${FILENAME}.desktop

	chmod 770 ${FILENAME}.desktop
}


# icon -n "${nickname}aya" ${PROJECT_NAME} ${PROJECT_PATH} Maya pipe/tools/_resources/dcc-maya-icon.png launch/unix/maya.sh
# icon -n "${nickname}ini" ${PROJECT_NAME} ${PROJECT_PATH} Houdini pipe/tools/_resources/dcc-houdini-icon.png launch/unix/hou.sh
# icon -n "${nickname}uke" ${PROJECT_NAME} ${PROJECT_PATH} Nuke pipe/tools/_resources/1.png launch/unix/nuke.sh
icon -n "${nickname}stancePainter" ${PROJECT_NAME} ${PROJECT_PATH} SubstancePainter pipe/tools/_resources/dcc-substancePainter-icon.png launch/unix/sbs.sh
