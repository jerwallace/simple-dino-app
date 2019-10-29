execute_process(COMMAND "/home/jetbot/simple-dino-app/robot_ws/build/dinoapp/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/jetbot/simple-dino-app/robot_ws/build/dinoapp/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
