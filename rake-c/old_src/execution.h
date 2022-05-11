#ifndef EXECUTION_H
#define EXECUTION_H
#include "rake-c.h"
#include <sys/stat.h>
#include <unistd.h>


extern void perform_actions(ACTION_SET *);
extern int  check_file_exists(char *);

#endif