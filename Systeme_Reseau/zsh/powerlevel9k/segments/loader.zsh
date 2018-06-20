load_segments() {
    for segment in ${@}; do
        source ${POWERLEVEL9K_EXTERNAL_SEGMENTS}/${segment}.zsh
    done
}
