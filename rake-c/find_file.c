#include  <stdio.h>
#include  <stdlib.h>
#include  <sys/stat.h>
#include  <sys/types.h>
#include  <dirent.h>
#include  <sys/param.h>
#include  <string.h>

#if defined(__linux__)
extern         char *strdup(const char *s);
#endif

#define STRCMP(p, q)   (strcmp(p, q) == 0)

// char *result;

//  SCANS DIRECTORY RECURSIVELY 
int find_file(char *filename, char *buffer, char *dirname)
{
    DIR             *dirp;
    struct dirent   *dp;

    //  ENSURE THAT WE CAN OPEN (read-only) THE REQUIRED DIRECTORY
    dirp       = opendir(dirname);

    if (dirp == NULL) 
    {   
        
        perror( dirname );
        exit(EXIT_FAILURE);
    }

    //  READ FROM THE REQUIRED DIRECTORY, UNTIL WE REACH ITS END
    while((dp = readdir(dirp)) != NULL) 
    {
        struct stat     stat_info;
        char            pathname[MAXPATHLEN];

        //  SENDS FORMATTED STRING TO STRING POINTER POINTED BY pathname
        sprintf(pathname, "%s/%s", dirname, dp->d_name);
        //printf("%s\n", pathname);
        //  DETERMINE ATTRIBUTES OF THIS DIRECTORY ENTRY
        if(stat(pathname, &stat_info) != 0) 
        {
            perror( pathname );
            exit(EXIT_FAILURE);
        }

        //  CHECKS IF FILE IS A DIRECTORY AND RECURSIVELY READS FILES 
        if( S_ISDIR(stat_info.st_mode) 
            && (!STRCMP(dp->d_name, ".")) 
            && (!STRCMP(dp->d_name, "..")) )
        {
            find_file(filename, buffer, pathname);
        }

        else if ( STRCMP(dp->d_name, filename) && STRCMP(dp->d_name, ".") )
        {   
            printf("%s\n", pathname);
            buffer = strdup(pathname);

            // FOUND THE FILE
            return 0;
        }
    }
    
    //  CLOSE THE DIRECTORY
    closedir(dirp);

    // DIDNT FIND THE FILE
    return 1;
}

// int main(int argc, char const *argv[])
// {   
//     char *filename = "program.c";
//     char *dir = "../..";
//     char *buffer = "";
//     find_file(filename, buffer, dir);

//     //printf("%s\n", buffer);

//     return 0;
// }
