
     download the shellscript:                          genrake.sh
     make a new directory, and move the shellscript to that directory
     make the shellscript executable:                   chmod 700 genrake.sh
     generate the files:                                ./genrake.sh 10
     see what was generated:                            ls -l
     edit Rakefile10 to set your values of HOSTS

     compile everything with your rake client:          ...somewhere/rake-c Rakefile10
     (if all went well) make the program executable:    chmod 700 program10
     run your compiled program:                         ./program10
     the answer should be 385

     cleanup:                                           make -f Makefile10 clean


