#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

//  strsplit.c (v0.1), written by Chris.McDonald@uwa.edu.au, 2006-
//  under licence - creativecommons.org/licenses/by-nc-sa/4.0/

#if     defined(__linux__)
extern  char    *strdup(const char *str);
#endif

#define SQUOTE          '\''
#define DQUOTE          '"'

char **strsplit(const char *str, int *nwords)
{
    char **words    = NULL;
    *nwords         = 0;

    char    *copy   = strdup(str);

    if(copy != NULL) {
        char    *startcopy = copy;

        while(*copy) {
            char *start;

//  SKIP LEADING WHITESPACE
            while(*copy == ' ' || *copy == '\t') {
                ++copy;
            }
            if(*copy == '\0') {
                break;
            }

//  COLLECT NEXT WORD - A QUOTED STRING WHICH CAN INCLUDE WHITESPACE
            if(*copy == SQUOTE || *copy == DQUOTE) {
                char quote  = *copy;

                start = ++copy;
                while(*copy && *copy != quote) {
                    ++copy;
                }
                if(*copy == '\0') {     // no closing quote?
                    break;
                }
                *copy++ = '\0';         // terminate string to be copied
            }
//  COLLECT NEXT WORD - AN UNQUOTED STRING
            else {
                start = copy;
                while(*copy && (*copy != ' ' && *copy != '\t')) {
                    ++copy;
                }
                if(copy == start) {
                    break;
                }
                if(*copy != '\0') {
                    *copy++ = '\0';     // terminate string to be copied
                }
            }

//  DUPLICATE THE STRING    t <- [start..copy]
            char *word  = strdup(start);
            if(word) {
                words   = realloc(words, (*nwords+2)*sizeof(words[0]));
                if(words) {
                    words[*nwords]  = word;
                    *nwords += 1;
                    words[*nwords]  = NULL;
                }
                else {
                    free(word);
                    word   = NULL;
                }
            }

//  ANY ERRORS?  DEALLOCATE MEMORY BEFORE RETURNING
            if(word == NULL) {
                if(words) {
                    for(int w=0 ; w < *nwords ; ++w) {
                        free(words[w]);
                    }
                    free(words);
                }
                words   = NULL;
                *nwords = 0;
                break;
            }
        }
        free(startcopy);
    }
    return words;
}

void free_words(char **words)
{
    if(words != NULL) {
        char	**t = words;

        while(*t) {
            free(*t++);
        }
        free(words);
    }
}

//  vim: ts=8 sw=4
