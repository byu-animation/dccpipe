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

if [[ ! -d ${PROJECT_PATH} ]]; then
	echo "error: project directory '${PROJECT_PATH}' does not exist."
	exit 1
fi

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
	NOSPACES_PROJECT=${PROJECT_NAME// /-}
	FILENAME=${PROJECT_PATH}"/dcc_${NOSPACES_PROJECT,,}_${NOSPACES,,}.desktop"

	echo "#!/usr/bin/env xdg-open" > ${FILENAME}
	echo "[Desktop Entry]" >> ${FILENAME}
	echo "Version=0.1" >> ${FILENAME}
	echo "Name=${PROGRAM_NAME}" >> ${FILENAME}
	echo "Name[en_US]=${PROGRAM_NAME}" >> ${FILENAME}
	echo "Comment=DCC Pipe shortcut for ${SOFTWARE_NAME}" >> ${FILENAME}
	echo "Exec=${PROJECT_PATH}/${SCRIPT}" >> ${FILENAME}
	echo "Icon=${PROJECT_PATH}/${ICON}" >> ${FILENAME}
	echo "Terminal=false" >> ${FILENAME}
	echo "Type=Application" >> ${FILENAME}
	echo "Categories=Utility;Application;" >> ${FILENAME}

	chmod 770 ${FILENAME}
}


icon -n "${nickname}aya" ${PROJECT_NAME} ${PROJECT_PATH} Maya pipe/tools/_resources/dcc-maya-icon.png launch/unix/maya.sh
icon -n "${nickname}ini" ${PROJECT_NAME} ${PROJECT_PATH} Houdini pipe/tools/_resources/dcc-houdini-icon.png launch/unix/hou.sh
icon -n "${nickname}uke" ${PROJECT_NAME} ${PROJECT_PATH} Nuke pipe/tools/_resources/dcc-nuke-icon.png launch/unix/nuke.sh
icon -n "${nickname}stancePainter" ${PROJECT_NAME} ${PROJECT_PATH} SubstancePainter pipe/tools/_resources/dcc-substancePainter-icon.png launch/unix/sbs.sh
