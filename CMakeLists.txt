cmake_minimum_required(VERSION 3.12)
project(rpi_cmd)
set(CMAKE_CXX_STANDARD 17)

add_executable(cmd_receiver cmd_receiver.cpp)
# ビルドコマンド:
#   mkdir build && cd build && cmake .. && make
