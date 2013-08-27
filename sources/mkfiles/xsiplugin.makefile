XSIINC=-I/software/Softimage/Softimage_2010_SP1/XSISDK/include
XSILIB=-L/software/Softimage/Softimage_2010_SP1/Application/bin -lsicppsdk -lsicoresdk

CC=gcc
CFLAGS=-m64 -c -Wfatal-errors -fPIC $(XSIINC)
LDFLAGS=-lm -lstdc++ $(XSILIB)
OBJECTS=$(SOURCES:.cpp=.o)
OUTDIR=../../build/opt/linux64/lib

all: $(SOURCES) $(OUTPUTFILE)
	
$(OUTPUTFILE): $(OBJECTS)
	mkdir -p $(OUTDIR)
	$(CC) -shared -Wl,-soname,$(OUTDIR)/lib$(OUTPUTFILE).so -o $(OUTDIR)/lib$(OUTPUTFILE).so $(OBJECTS)

.cpp.o:
	$(CC) $(CFLAGS) $(LDFLAGS) $< -o $@

clean:
	rm -f ../../build/opt/linux64/lib/$(OUTPUTFILE).a	rm -f $(OBJECTS)
