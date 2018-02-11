SRCS1=patchmatch.cpp
SRCS2=patchmatch_reversed.cpp
SRCS3=./tool/patchmatch.cpp

EXT=`python3-config --extension-suffix`

./tool/patchmatch$(EXT): $(SRCS3) patchmatch$(EXT)
	c++ -O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes` $(SRCS3) -o ./tool/patchmatch`python3-config --extension-suffix`

patchmatch$(EXT): $(SRCS1) patchmatch_reversed$(EXT)
	c++ -O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes` $(SRCS1) -o patchmatch`python3-config --extension-suffix`

patchmatch_reversed$(EXT): $(SRCS2)
	c++ -O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes` $(SRCS2) -o patchmatch_reversed`python3-config --extension-suffix`
