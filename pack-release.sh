#! /bin/bash
#
# package pykit and release to pypi source

pack_release()
{
    echo -e "Installing git and python-pip ...\n"
    yum install -y git python-pip 1> /dev/null

    echo -e "Upgrading setuptools, wheel and twine ...\n"
    pip install --upgrade setuptools wheel twine \
        -i https://pypi.douban.com/simplepip install --upgrade setuptools wheel twine 1> /dev/null

    echo -e "Configing environment to package pykit ...\n"

    if [[ -d /tmp/pykit  ]];then
        echo -e "\033[31m /tmp/pykit has been existed \033[0m"
        exit -1
    fi

    mkdir /tmp/pykit
    cp -r ../pykit /tmp/pykit/
    cd /tmp/pykit
    cp pykit/LICENSE pykit/README.md pykit/requirements.txt pykit/setup.py .

    echo -e "Packaging the pykit ...\n"
    python setup.py sdist bdist_wheel 1> /dev/null

    echo -e "Releasing the pykit ...\n"
    twine upload -u ${USER} -p ${PASS} dist/*
    cd -
    rm -rf /tmp/pykit
}

main()
{
    read -p "Please input the PyPI username:" USER
    read -s -p "Please input the password:" PASS
    pack_release ${USER} ${PASS}
}

main
