#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
    DESTDIR_ARG="--root=$DESTDIR"
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/jetbot/simple-dino-app/robot_ws/src/dinoapp"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/jetbot/simple-dino-app/robot_ws/install/dinoapp/lib/python2.7/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/jetbot/simple-dino-app/robot_ws/install/dinoapp/lib/python2.7/dist-packages:/home/jetbot/simple-dino-app/robot_ws/build/dinoapp/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/jetbot/simple-dino-app/robot_ws/build/dinoapp" \
    "/usr/bin/python2" \
    "/home/jetbot/simple-dino-app/robot_ws/src/dinoapp/setup.py" \
    build --build-base "/home/jetbot/simple-dino-app/robot_ws/build/dinoapp" \
    install \
    $DESTDIR_ARG \
    --install-layout=deb --prefix="/home/jetbot/simple-dino-app/robot_ws/install/dinoapp" --install-scripts="/home/jetbot/simple-dino-app/robot_ws/install/dinoapp/bin"
