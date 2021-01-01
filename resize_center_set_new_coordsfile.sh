#!/usr/bin/env bash


FILES_LOC="$HOME/.config"


function select_coords_file() {
    cd $FILES_LOC || return 10
    CMD=""
    for I in $( ls -1 resize_center_window_* ); do
        LN="$I $(cat $FILES_LOC/$I)"
        CMD="$CMD $LN"
    done
    COORDS_FILE=$(zenity --list --title "Select new coords file" --text "Current coords: $(cat resize_center_window.txt)" --column='file' --column='width' --column='height' $CMD)
    RC=$?
    [ $RC -ne 0 ] && { COORDS_FILE=""; }
    return $RC
}

function main() {
    if select_coords_file; then
        cd $FILES_LOC || return 10
        [ -r "$COORDS_FILE" ] || { echo "Selected file '$FILES_LOC/$COORDS_FILE' doesn't exists."; return 10; }
        rm -f "resize_center_window.txt.bak"
        mv -v "resize_center_window.txt" "resize_center_window.txt.bak" || return $?
        cp -v $COORDS_FILE "resize_center_window.txt" || return $?
    fi
}

main || { RC=$?; echo "Script failed"; exit $RC; }
echo "Script finished successfully"
