
function _make_build_image () {
    docker build \
        -t rebase/build \
        docker/build
}


function _rq-population-wheel () {
    _run \
        /venv/rq/bin/python \
            docker/rq_population/setup.py \
                bdist_wheel \
                    --bdist-dir /wheelhouse/bdist \
                    --dist-dir /wheelhouse/wheels
}

function _run () {
    docker run \
        --name build \
        -it \
        --rm \
        --volume /wheelhouse:/wheelhouse:rw \
        --volume $PWD:/api \
        --volume /var/run/docker.sock:/var/run/docker.sock \
        rebase/build $*
}

function _build-dev () {
    _run docker/build/build-dev
}

function _build-pro () {
    _run docker/build/build-pro
}
