#!/bin/bash

set -e

function download() {

   url=$1
   name=$2

   if [ -f "`pwd`/${name}" ]; then
        ctx logger info "`pwd`/${name} already exists, No need to download"
   else
        # download to given directory
        ctx logger info "Downloading ${url} to `pwd`/${name}"

        set +e
        curl_cmd=$(which curl)
        wget_cmd=$(which wget)
        set -e

        if [[ ! -z ${curl_cmd} ]]; then
            curl -L -o ${name} ${url}
        elif [[ ! -z ${wget_cmd} ]]; then
            wget -c -O ${name} ${url}
        else
            ctx logger error "Failed to download ${url}: Neither 'cURL' nor 'wget' were found on the system"
            exit 1;
        fi
   fi

}


function untar() {

    tar_archive=$1
    destination=$2

    if [ ! -d ${destination} ]; then
        inner_name=$(tar -tf "${tar_archive}" | grep -o '^[^/]\+' | sort -u)
        ctx logger info "Untaring ${tar_archive}"
        tar -zxvf ${tar_archive}

        ctx logger info "Moving ${inner_name} to ${destination}"
        mv ${inner_name} ${destination}
    fi
}

TEMP_DIR="${HOME}/$(ctx execution-id)/"
MONGO_TARBALL_NAME='mongodb-linux-x86_64-2.4.9.tgz'

################################
# Directory that will contain:
#  - MongoDB binaries
#  - MongoDB Database files
################################
MONGO_ROOT_PATH=${TEMP_DIR}/mongodb
MONGO_DATA_PATH=${MONGO_ROOT_PATH}/data
MONGO_BINARIES_PATH=${MONGO_ROOT_PATH}/mongodb-binaries
mkdir -p ${MONGO_ROOT_PATH}

cd ${TEMP_DIR}
download http://downloads.mongodb.org/linux/${MONGO_TARBALL_NAME} ${MONGO_TARBALL_NAME}
untar ${MONGO_TARBALL_NAME} ${MONGO_BINARIES_PATH}

echo "Creating MongoDB data directory in ${MONGO_DATA_PATH}"
mkdir -p ${MONGO_DATA_PATH}

ctx logger info "Sucessfully installed MongoDB"

function get_response_code() {

    port=$1

    set +e

    curl_cmd=$(which curl)
    wget_cmd=$(which wget)

    if [[ ! -z ${curl_cmd} ]]; then
        response_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${port})
    elif [[ ! -z ${wget_cmd} ]]; then
        response_code=$(wget --spider -S "http://localhost:${port}" 2>&1 | grep "HTTP/" | awk '{print $2}' | tail -1)
    else
        ctx logger error "Failed to retrieve response code from http://localhost:${port}: Neither 'cURL' nor 'wget' were found on the system"
        exit 1;
    fi

    set -e

    echo ${response_code}

}

function wait_for_server() {

    port=$1
    server_name=$2

    started=false

    ctx logger info "Running ${server_name} liveness detection on port ${port}"

    for i in $(seq 1 120)
    do
        response_code=$(get_response_code ${port})
        ctx logger info "[GET] http://localhost:${port} ${response_code}"
        if [ ${response_code} -eq 200 ] ; then
            started=true
            break
        else
            ctx logger info "${server_name} has not started. waiting..."
            sleep 1
        fi
    done
    if [ ${started} = false ]; then
        ctx logger error "${server_name} failed to start. waited for a 120 seconds."
        exit 1
    fi
}

PORT=27017
COMMAND="${MONGO_BINARIES_PATH}/bin/mongod --port ${PORT} --dbpath ${MONGO_DATA_PATH} --rest --journal --shardsvr --smallfiles"

rm -f ${HOME}/mongo-nodecellar.conf

ctx logger info "${COMMAND}"

echo -e "description 'mongo nodecellar service'
# used to be: start on startup
# until we found some mounts were not ready yet while booting
start on started mountall
stop on shutdown
# Automatically Respawn:
respawn
respawn limit 99 5
setuid ubuntu
setgid ubuntu
script
    exec ${COMMAND} 2>&1
end script\n" >> ${HOME}/mongo-nodecellar.conf

init-checkconf -d ${HOME}/mongo-nodecellar.conf

sudo cp ${HOME}/mongo-nodecellar.conf /etc/init/mongo-nodecellar.conf

sudo chown root:root /etc/init/mongo-nodecellar.conf

# run service

sudo initctl start mongo-nodecellar

ctx logger info "Sucessfully started MongoDB"


MONGO_REST_PORT=`expr ${PORT} + 1000`
wait_for_server ${MONGO_REST_PORT} 'MongoDB'
