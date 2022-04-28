#include <stdio.h>
#include <stdlib.h> 
#include <string.h>
#include <ctype.h>

#define MAX_LINE_LENGTH 80

void file_process(char *file_name)
{
    FILE *fp = fopen(file_name, "r");
    if(fp == NULL)
    {
        fprintf(stderr, "Invalid file\n");
    }
    else
    {
        char line[MAX_LINE_LENGTH] = "";
        // READ AND PARSE FILES LINE BY LINE
        while(fgets(line, MAX_LINE_LENGTH, fp))
        {
            if (line[0] == '#')
            {
                continue;
            }

			if (line[0] == '\t')
			{
				printf("action\n");
			
			}

            if (line[0] == '\t' && line[1] == '\t') 
            {
				printf("Req prog\n");

            }

			
        }
    }

}

int main (int argc, char *argv[])
{
    char* file_name = argv[1];
    file_process(file_name);

    return 0; 
}