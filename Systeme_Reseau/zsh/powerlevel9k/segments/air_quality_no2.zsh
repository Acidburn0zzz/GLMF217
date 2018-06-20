no2_index() {
  local len=${#POWERLEVEL9K_AIR_QUALITY_INDEX_RANGE[@]}
  local result=false

  for (( i=1; i<=${len}; i++ )); do
    if (( ($1 + 0.0) < ${POWERLEVEL9K_AIR_QUALITY_INDEX_RANGE[$i]} )); then
      echo -n ${i}
      result=true
      break
    fi
  done

  if [[ ! ${result} ]]; then
    echo -n ${len}
  fi
}

prompt_air_quality_no2() {
  local search=true

  if [ -f ${POWERLEVEL9K_AIR_QUALITY_TMP}/aq_no2.json ]; then 
    local age=$(stat -c %Y ${POWERLEVEL9K_AIR_QUALITY_TMP}/aq_no2.json)
    local now=$(date +%s)
    if [ $(( now - age )) -lt ${POWERLEVEL9K_AIR_QUALITY_TIME} ]; then
        search=false
    fi
  fi

  if [ ${search} = true ]; then
    local today=$(date +%F)
    curl -s "https://api.openaq.org/v1/measurements?location=${POWERLEVEL9K_AIR_QUALITY_LOCATION}&date_from=${today}&limit=1&parameter=no2" -o ${POWERLEVEL9K_AIR_QUALITY_TMP}/aq_no2.json
    no2=$(cat ${POWERLEVEL9K_AIR_QUALITY_TMP}/aq_no2.json  | python3 -c "import sys, json; print(json.load(sys.stdin)['results'][0]['value'])")
    echo ${no2} > ${POWERLEVEL9K_AIR_QUALITY_TMP}/aq_no2.txt
  fi

  local value=$(cat ${POWERLEVEL9K_AIR_QUALITY_TMP}/aq_no2.txt)
  local index=$(no2_index ${value})
  local bg_color="${POWERLEVEL9K_AIR_QUALITY_BACKGROUND_RANGE[${index}]}"
  local fg_color="${POWERLEVEL9K_AIR_QUALITY_FOREGROUND_RANGE[${index}]}"
  local content="%{%K{$bg_color}%}%{%F{$fg_color}%}NO\u2082: ${value}\u00b5g/m\u00b3"
  $1_prompt_segment "$0" "$2" ${bg_color} ${fg_color} ${content} "###"
}

POWERLEVEL9K_AIR_QUALITY_TMP=${HOME}/.powerlevel9k/segments/tmp
POWERLEVEL9K_AIR_QUALITY_TIME=3600
POWERLEVEL9K_AIR_QUALITY_ONLY_WARNING=false
POWERLEVEL9K_AIR_QUALITY_INDEX_RANGE=(50 100 140 200 400)
POWERLEVEL9K_AIR_QUALITY_FOREGROUND_RANGE=(255 255 255 255 234 234)
POWERLEVEL9K_AIR_QUALITY_BACKGROUND_RANGE=(022 028 034 226 214 196)
POWERLEVEL9K_AIR_QUALITY_LOCATION="FR03014"
POWERLEVEL9K_AIR_QUALITY_NO2="prompt_air_quality_no2"
